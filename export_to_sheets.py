import sqlite3
import gspread

import os
import json

def export_db_to_sheets(date_label=None, source_url=None):
    print("Connecting to Google Sheets...")
    
    creds_json = os.environ.get('GCP_CREDENTIALS')
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            # Fix for JWT signature errors: ensure newlines are correctly formatted
            if 'private_key' in creds_dict:
                creds_dict['private_key'] = creds_dict['private_key'].replace("\\n", "\n")
            gc = gspread.service_account_from_dict(creds_dict)
            print("Authenticated using GCP_CREDENTIALS environment variable (sanitized).")
        except Exception as e:
            print(f"Error parsing GCP_CREDENTIALS env var: {e}")
            gc = gspread.service_account(filename='credentials.json')
    else:
        gc = gspread.service_account(filename='credentials.json')
    
    print("Opening the existing Google Sheet...")
    # Open the sheet using its URL or ID
    sh = gc.open_by_key('1bPhadhGcRUMPp-xsKcWx5M9LFQ_sheHoYbtZJEPMQ0g')
    
    print("Connecting to sqlite database...")
    conn = sqlite3.connect('volleyball.db')
    c = conn.cursor()
    
    # Get all courts, enforcing 'Main' to the top of the list, then alphabetizing the rest
    c.execute('''
        SELECT id, name FROM courts 
        ORDER BY 
            CASE WHEN name LIKE 'Main%' THEN 0 ELSE 1 END,
            name ASC
    ''')
    courts = c.fetchall()
    
    # Get all distinct time slots for the header
    c.execute("SELECT DISTINCT time_slot FROM slots ORDER BY id") 
    time_slots = [row[0] for row in c.fetchall()]
    
    import datetime
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
                c.execute("SELECT status FROM slots WHERE court_id = ? AND time_slot = ?", (court_id, ts))
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
    
    print("Data export complete!")

if __name__ == '__main__':
    export_db_to_sheets()
