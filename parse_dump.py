from bs4 import BeautifulSoup

with open('debug_dump.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')
results = soup.select('.result-content')
if not results:
    results = soup.select('table#frwebsearch_output_table')

for res in results:
    h2 = res.find('h2')
    if not h2: continue
    facility_name = h2.get_text(strip=True)
    if "Beach Volleyball Court" not in facility_name:
        continue
    
    slots = res.select('.cart-blocks a.button')
    print(f"Court: {facility_name}, Slots: {len(slots)}")
    for slot in slots:
        time_text = slot.get_text(separator=" ", strip=True)
        classes = slot.get('class', [])
        is_booked = 'error' in classes
        print(f"  {time_text} -> booked: {is_booked} ({classes})")
    break # Just show the first court
