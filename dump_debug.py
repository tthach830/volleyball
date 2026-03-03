from playwright.sync_api import sync_playwright
import datetime
import sys

def dump_html(target_date):
    date_obj = datetime.datetime.strptime(target_date, "%m%d%Y")
    url_date = date_obj.strftime("%m%%2F%d%%2F%Y")
    
    base_url = "https://casantacruzweb.myvscloud.com/webtrac/web/search.html?Action=Start&SubAction=&_csrf_token=xk0W0R6N0C712M2S3A2O2E4A4P4H6O6A055Q5H505203035W595T1B6W3Q6I581C5I4P4O6A1H5I4V57536M6S4J5K69016W5W6M5V17704M5D68076D4E6G471C5V4J6J&date="
    end_url = "&keyword=&primarycode=&frheadcount=0&type=Beach+Volleyball+Court&frclass=&keywordoption=Match+One&blockstodisplay=15&features1=&features2=&features3=&features4=&features5=&features6=&features7=&features8=&begintime=12%3A00+am&subtype=&category=&features=&display=Detail&module=FR&multiselectlist_value=&frwebsearch_buttonsearch=yes"
    
    target_url = base_url + url_date + end_url
    print(f"Dumping HTML for {target_date}...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(target_url, wait_until="networkidle", timeout=60000)
        
        # Wait for the grid
        page.wait_for_timeout(10000)
        
        content = page.content()
        with open('c:/volleyball/debug_dump.html', 'w', encoding='utf-8') as f:
            f.write(content)
            
        browser.close()
    print("Done. Saved to debug_dump.html")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else '03022026'
    dump_html(target)
