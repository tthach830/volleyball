import sqlite3
import gspread

import os
import json
import datetime

def export_db_to_sheets(date_label=None, source_url=None, target_date_str=None):
    if not target_date_str:
        import datetime
        target_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    print("Connecting to Google Sheets...")
    
    # 1. Try local file first (best for local development)
    if os.path.exists('credentials.json'):
        try:
            gc = gspread.service_account(filename='credentials.json')
            print("Authenticated using local credentials.json file.")
        except Exception as e:
            print(f"Error loading local credentials.json: {e}")
            gc = None
    else:
        gc = None

    # 2. Fallback to environment variable (best for GitHub Actions)
    if gc is None:
        creds_json = os.environ.get('GCP_CREDENTIALS', '').strip()
        
        # Remove surrounding quotes if added by the environment
        if creds_json.startswith('"') and creds_json.endswith('"'):
            creds_json = creds_json[1:-1]

        if creds_json:
            try:
                import base64
                # Try to decode as Base64 first in case the user chose that robust path
                try:
                    if not creds_json.startswith('{'):
                        creds_json = base64.b64decode(creds_json).decode('utf-8')
                        print("Decoded GCP_CREDENTIALS from Base64.")
                except:
                    pass

                creds_dict = json.loads(creds_json)
                # Robust private key sanitization
                if 'private_key' in creds_dict:
                    pk = creds_dict['private_key']
                    # Fix escaped newlines common in CI/CD
                    pk = pk.replace("\\n", "\n")
                    # Strip potential hidden whitespace
                    pk = pk.strip()
                    creds_dict['private_key'] = pk
                    
                gc = gspread.service_account_from_dict(creds_dict)
                print("Authenticated using GCP_CREDENTIALS environment variable (robustly parsed).")
            except Exception as e:
                print(f"Error parsing GCP_CREDENTIALS env var: {e}")
                raise Exception("Could not authenticate: No valid credentials found.")
        else:
            raise Exception("Could not authenticate: credentials.json not found and GCP_CREDENTIALS not set.")
    
    print("Opening the existing Google Sheet...")
    # Open the sheet using its URL or ID
    sh = gc.open_by_key('1bPhadhGcRUMPp-xsKcWx5M9LFQ_sheHoYbtZJEPMQ0g')
    
    print("Connecting to sqlite database...")
    conn = sqlite3.connect('volleyball.db')
    c = conn.cursor()
    
    # Check if the courts table exists to avoid OperationalError
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='courts'")
    if not c.fetchone():
        print("Table 'courts' does not exist yet. This usually happens if the first scrape failed. Skipping export.")
        conn.close()
        return

    # Get all courts, enforcing 'Main' to the top of the list, then alphabetizing the rest
    c.execute('''
        SELECT id, name FROM courts 
        ORDER BY 
            CASE WHEN name LIKE 'Main%' THEN 0 ELSE 1 END,
            name ASC
    ''')
    courts = c.fetchall()
    
    if not courts:
        print("No courts found in database. Skipping export.")
        conn.close()
        return

    # Get all distinct time slots for the header
    c.execute("SELECT DISTINCT time_slot FROM slots ORDER BY id") 
    time_slots = [row[0] for row in c.fetchall()]
    
    if not time_slots:
        # If we have courts but no slots (e.g. Dream courts only), we still need some slots to show
        # but for now, let's just warn and exit to keep it simple
        print("No time slots found. Skipping export.")
        conn.close()
        return
    
    if not date_label:
        today = datetime.datetime.now()
        date_label = today.strftime("%B %d")
    
    worksheet = sh.sheet1
    print("Writing data to the sheet...")
    
    # A1: Clickable hyperlink titled "Court (March 10)" linking to the WebTrac scrape URL
    link_label = f"Court ({date_label})"
    if source_url:
        worksheet.update(
            range_name='A1',
            values=[[f'=HYPERLINK("{source_url}", "{link_label}")']], 
            value_input_option='USER_ENTERED'
        )
    else:
        worksheet.update_acell('A1', link_label)
    
    # B1 onward: time slot headers (row 1)
    headers = ["LastUpdated"] + time_slots
    worksheet.update(range_name='B1', values=[headers])
    
    now = datetime.datetime.now()
    timestamp_str = now.strftime("%b {day}, {hour}:%M %p").format(day=now.day, hour=now.hour % 12 or 12)

    # A2 onward: court rows (name + LastUpdated + slot statuses), no leading header row
    court_rows = []
    for court_id, court_name in courts:
        display_name = court_name.replace("Main Beach Volleyball Court", "Main")
        row = [display_name]
        
        lower_name = court_name.lower()
        if "main" in lower_name:
            row.append(timestamp_str)
        else:
            row.append("-")
            
        for ts in time_slots:
            if "main" not in court_name.lower():
                row.append("available")
            else:
                c.execute("SELECT status FROM slots WHERE court_id = ? AND time_slot = ? AND (date = ? OR date IS NULL)", (court_id, ts, target_date_str))
                res = c.fetchone()
                row.append(res[0] if res else "N/A")
        court_rows.append(row)
    worksheet.update(range_name='A2', values=court_rows)
    
    print("Applying conditional formatting...")
    # Add conditional formatting for "unavailable" using the raw Google Sheets API
    sheet_id = worksheet.id
    body = {
        "requests": [
            {
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [
                            {
                                "sheetId": sheet_id,
                                "startRowIndex": 1,
                                "endRowIndex": len(courts) + 1,
                                "startColumnIndex": 2,
                                "endColumnIndex": len(time_slots) + 2
                            }
                        ],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_CONTAINS",
                                "values": [{"userEnteredValue": "unavailable"}]
                            },
                            "format": {
                                "backgroundColor": {
                                    "red": 1.0,
                                    "green": 0.4,
                                    "blue": 0.4
                                }
                            }
                        }
                    },
                    "index": 0
                }
            }
        ]
    }
    sh.batch_update(body)
    
    print("Writing data to the History sheet...")
    try:
        history_sheet = sh.worksheet("History")
    except gspread.exceptions.WorksheetNotFound:
        history_sheet = sh.add_worksheet(title="History", rows="1000", cols="5")
        history_sheet.append_row(["Scrape Timestamp", "Date", "Court", "Time Slot", "Status"])

    c.execute('''
        SELECT c.name, s.time_slot, s.status
        FROM slots s
        JOIN courts c ON s.court_id = c.id
        WHERE s.date = ? OR s.date IS NULL
        ORDER BY c.name, s.id
    ''', (target_date_str,))
    history_data = c.fetchall()

    if history_data:
        scrape_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        append_data = []
        for row in history_data:
            # We don't want to export Dream/Harbor empty slots to history unless they have real status
            # But the requirement implies exporting what we scraped
            # Actually, let's only log Main courts to history to save space, or log them all. Let's log them all.
            append_data.append([scrape_timestamp, target_date_str, row[0], row[1], row[2]])
        
        history_sheet.append_rows(append_data)
        print(f"Appended {len(append_data)} rows to History sheet.")

    print("Data export complete!")

if __name__ == '__main__':
    export_db_to_sheets()
