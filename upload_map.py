import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.http
import os
import time

def upload_map_to_sheets():
    file_id = '1B-C4aK_dOqIB1Ze8ChJ1lAdywZ5EN5m_'
    spreadsheet_id = '1bPhadhGcRUMPp-xsKcWx5M9LFQ_sheHoYbtZJEPMQ0g'
    
    print("Authenticating with Google Drive and Sheets...")
    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ]
    
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
                
            creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
            print("Authenticated using GCP_CREDENTIALS environment variable (robustly parsed).")
        except Exception as e:
            print(f"Error parsing GCP_CREDENTIALS env var: {e}")
            creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=scopes)
    else:
        creds = service_account.Credentials.from_service_account_file('credentials.json', scopes=scopes)
    
    # 1. Update existing file on Drive
    print(f"Updating existing map image on Google Drive (ID: {file_id})...")
    drive_service = build('drive', 'v3', credentials=creds)
    
    media = googleapiclient.http.MediaFileUpload('map_status.png', mimetype='image/png')
    
    try:
        # We use update instead of create to use the user's quota
        file = drive_service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()
        print(f"Successfully updated Drive file content.")
    except Exception as e:
        print(f"Error updating Drive file: {e}")
        print("Make sure you shared the file with the service account as an 'Editor'.")
        return
    
    # Ensure it is publicly readable for the =IMAGE() formula
    try:
        permission = {
            'type': 'anyone',
            'role': 'reader'
        }
        drive_service.permissions().create(
            fileId=file_id,
            body=permission,
            fields='id'
        ).execute()
        print("Set permissions to anyone with link.")
    except Exception as e:
        print(f"Note: Could not set extra permissions (might be disabled by organization or already set): {e}")

    # Add timestamp to bust the image cache so Map sheet always shows latest
    ts = int(time.time())
    public_url = f"https://drive.google.com/uc?export=view&id={file_id}&t={ts}"
    view_url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    
    # 2. Insert into Google Sheets
    print("Opening Google Sheet...")
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(spreadsheet_id)
    
    try:
        map_sheet = sh.worksheet("Map")
    except gspread.exceptions.WorksheetNotFound:
        print("Worksheet 'Map' not found. Creating it...")
        map_sheet = sh.add_worksheet(title="Map", rows="100", cols="20")
    
    map_sheet.clear()
    
    print("Writing hyperlink and image formula to the Map sheet...")
    # Add a clickable hyperlink in A1 (USER_ENTERED so formula is evaluated)
    map_sheet.update(
        range_name='A1',
        values=[[f'=HYPERLINK("{view_url}", "Click here to view Full Resolution Map")']],
        value_input_option='USER_ENTERED'
    )
    
    # Insert the image in A2 with cache-busting timestamp URL
    map_sheet.update(
        range_name='A2',
        values=[[f'=IMAGE("{public_url}", 4, 800, 1200)']],
        value_input_option='USER_ENTERED'
    )
    
    # Resize the cell so the image fits
    sheet_id = map_sheet.id
    body = {
        "requests": [
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": 1,
                        "endIndex": 2
                    },
                    "properties": {
                        "pixelSize": 800
                    },
                    "fields": "pixelSize"
                }
            },
            {
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1
                    },
                    "properties": {
                        "pixelSize": 1200
                    },
                    "fields": "pixelSize"
                }
            }
        ]
    }
    sh.batch_update(body)
    
    print("Map integration complete!")

if __name__ == '__main__':
    upload_map_to_sheets()
