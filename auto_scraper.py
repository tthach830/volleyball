import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import sqlite3
import export_to_sheets
import sys

def run_scraper(specific_date=None, target_sheet_name=None):
    # 1. Determine target date
    if specific_date:
        try:
            target_date = datetime.datetime.strptime(specific_date, "%m%d%Y")
        except ValueError:
            try:
                # Fallback to YYYY-MM-DD
                target_date = datetime.datetime.strptime(specific_date, "%Y-%m-%d")
            except ValueError:
                print(f"Error: Invalid date format '{specific_date}'. Please use MMDDYYYY or YYYY-MM-DD.")
                return
    else:
        target_date = datetime.datetime.now()

    url_date = target_date.strftime("%m%%2F%d%%2F%Y")
    display_date = target_date.strftime("%B %d, %Y")
    header_date = target_date.strftime("%B %d")
    
    base_url = "https://casantacruzweb.myvscloud.com/webtrac/web/search.html?Action=Start&SubAction=&_csrf_token=xk0W0R6N0C712M2S3A2O2E4A4P4H6O6A055Q5H505203035W595T1B6W3Q6I581C5I4P4O6A1H5I4V57536M6S4J5K69016W5W6M5V17704M5D68076D4E6G471C5V4J6J&date="
    end_url = "&keyword=&primarycode=&frheadcount=0&type=Beach+Volleyball+Court&frclass=&keywordoption=Match+One&blockstodisplay=15&features1=&features2=&features3=&features4=&features5=&features6=&features7=&features8=&begintime=12%3A00+am&subtype=&category=&features=&display=Detail&module=FR&multiselectlist_value=&frwebsearch_buttonsearch=yes"
    
    target_url = base_url + url_date + end_url
    print(f"Scraping availability for today: {display_date}")
    
    # 2. Ensure Database structure exists early
    conn = sqlite3.connect('volleyball.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS courts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            court_id INTEGER,
            time_slot TEXT,
            status TEXT,
            date TEXT,
            FOREIGN KEY(court_id) REFERENCES courts(id)
        )
    ''')
    
    # Safely migrate existing databases
    try:
        c.execute('ALTER TABLE slots ADD COLUMN date TEXT')
    except sqlite3.OperationalError:
        pass # Column already exists
    
    conn.commit()
    conn.close()

    # 3. Use Playwright to load the page and extract HTML
    print("Launching headless browser...")
    with sync_playwright() as p:
        # Some WebTrac portals block basic Headless Chrome signatures
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print(f"Navigating to {target_url}")
        
        try:
            # Load page and wait for general network quietness
            print(f"Navigating to {target_url}...")
            page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
            
            # Wait a few seconds for any dynamic JS to settle
            page.wait_for_timeout(5000)
            
            # WebTrac often uses a specific table or grid container that takes a moment to render
            print("Waiting for schedule grid to render...")
            
            # Wait for either the grid rows or a known "no results" message
            try:
                page.wait_for_selector('.ui-grid-row, .facility-schedule-block, table', timeout=20000)
            except:
                print("Specific grid selectors not found, falling back to static wait just in case...")
                page.wait_for_timeout(10000)
            
            html_content = page.content()
            
        except Exception as e:
            print(f"Error loading page or finding grid: {e}")
            page.screenshot(path="error_screenshot.png", full_page=True)
            print("Saved error screenshot to error_screenshot.png")
            html_content = page.content()
            
        browser.close()
        
    print("Browser closed. Parsing data...")
    
    # 3. Use BeautifulSoup to parse the layout
    soup = BeautifulSoup(html_content, 'html.parser')
    court_data = []
    
    # helper to explode time ranges like "4:00 pm - 6:00 pm" into individual hours
    def get_hours_in_range(time_range_str):
        # Clean the string (remove "Unavailable", etc.)
        clean_str = time_range_str.split('\n')[0].strip() # Handles some WebTrac multiline labels
        if ' - ' not in clean_str:
            return [clean_str]
            
        try:
            start_str, end_str = clean_str.split(' - ')
            start_dt = datetime.datetime.strptime(start_str.strip(), "%I:%M %p")
            end_dt = datetime.datetime.strptime(end_str.strip(), "%I:%M %p")
            
            hours = []
            current = start_dt
            while current < end_dt:
                next_hour = current + datetime.timedelta(hours=1)
                # Formats like '7am-8am' or '12pm-1pm'
                current_str = current.strftime('%#I%p').lower()
                next_str = next_hour.strftime('%#I%p').lower()
                hours.append(f"{current_str}-{next_str}")
                current = next_hour
            return hours
        except:
            return [clean_str]

    # Find all facility result items
    results = soup.select('.result-content')
    if not results:
        print("Error: No results found with '.result-content'. Trying fallback table search...")
        # Fallback if the site structure changes slightly
        results = soup.select('table#frwebsearch_output_table')

    for res in results:
        # Get Court Name
        h2 = res.find('h2')
        if not h2: continue
        facility_name = h2.get_text(strip=True)
        
        # Only process if it's one of our courts
        if "Beach Volleyball Court" not in facility_name:
            continue
            
        available_slots = []
        booked_slots = []
        
        # Find all slot buttons
        # Based on dump: <a class="button full-block success..." ...> 7:00 am - 8:00 am</a>
        # success = available, error = booked
        slots = res.select('.cart-blocks a.button')
        
        for slot in slots:
            time_text = slot.get_text(separator=" ", strip=True) # "4:00 pm - 6:00 pm Unavailable"
            # Remove the "Unavailable" or "Inquiry Only" text if present
            time_text = time_text.replace("Unavailable", "").replace("Inquiry Only", "").strip()
            
            classes = slot.get('class', [])
            is_booked = 'error' in classes
            
            exploded = get_hours_in_range(time_text)
            if is_booked:
                booked_slots.extend(exploded)
            else:
                available_slots.extend(exploded)
                
        if available_slots or booked_slots:
            court_data.append({
                "facility": facility_name,
                "available_slots": available_slots,
                "booked_slots": booked_slots
            })

    if not court_data:
        print("Error: Could not find court data on the page. The WebTrac layout may have changed.")
        # Save HTML for debugging if this happens
        with open('failed_parse_dump.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        return

    print("Data extracted successfully. Updating database...")
    
    # 4. Update Database
    conn = sqlite3.connect('volleyball.db')
    c = conn.cursor()
    
    # Clear old slots for this specific date only (so we can re-run same day safely)
    target_date_str = target_date.strftime("%Y-%m-%d")
    c.execute('DELETE FROM slots WHERE date = ? OR date IS NULL', (target_date_str,))
    
    for court in court_data:
        c.execute("INSERT OR IGNORE INTO courts (name) VALUES (?)", (court['facility'],))
        c.execute("SELECT id FROM courts WHERE name = ?", (court['facility'],))
        court_id = c.fetchone()[0]
        
        for slot in court['available_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status, date) VALUES (?, ?, ?, ?)", (court_id, slot, 'available', target_date_str))
            
        for slot in court['booked_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status, date) VALUES (?, ?, ?, ?)", (court_id, slot, 'reserved', target_date_str))
            
    # Inject Dream and Harbor courts as fully available for all generated timeslots
    c.execute("SELECT DISTINCT time_slot FROM slots")
    all_time_slots = [row[0] for row in c.fetchall()]
    
    extra_courts = ["Dream 1", "Dream 2", "Harbor 1", "Harbor 2", "Harbor 3", "Harbor 4"]
    for extra_court in extra_courts:
        c.execute("INSERT OR IGNORE INTO courts (name) VALUES (?)", (extra_court,))
        c.execute("SELECT id FROM courts WHERE name = ?", (extra_court,))
        court_id = c.fetchone()[0]
        for slot in all_time_slots:
            c.execute("INSERT INTO slots (court_id, time_slot, status, date) VALUES (?, ?, ?, ?)", (court_id, slot, 'available', target_date_str))
            
    conn.commit()
    conn.close()
    
    print("Database updated. Exporting to Google Sheets...")
    # 5. Export to Google Sheets
    export_to_sheets.export_db_to_sheets(date_label=header_date, source_url=target_url, target_date_str=target_date_str, target_sheet_name=target_sheet_name)
    
    print("Scraping and update complete!")

import argparse
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="WebTrac Court Availability Scraper")
    parser.add_argument("positional_date", nargs="?", help="Optional Target date in MMDDYYYY format for backward compatibility")
    parser.add_argument("--date", help="The target date to scrape (MMDDYYYY or YYYY-MM-DD format).")
    parser.add_argument("--sheetname", help="The specific name of the sheet to export data to.")
    args = parser.parse_args()
    
    date_arg = args.date if args.date else args.positional_date
    run_scraper(specific_date=date_arg, target_sheet_name=args.sheetname)