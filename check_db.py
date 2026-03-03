import sqlite3

def check_unavailable():
    conn = sqlite3.connect('c:/volleyball/volleyball.db')
    c = conn.cursor()
    c.execute("""
        SELECT courts.name, slots.time_slot 
        FROM slots 
        JOIN courts ON slots.court_id = courts.id 
        WHERE status = 'unavailable'
    """)
    rows = c.fetchall()
    if not rows:
        print("No unavailable slots found in database.")
    else:
        print(f"Found {len(rows)} unavailable slots:")
        for court, slot in rows:
            print(f" - {court}: {slot}")
    conn.close()

if __name__ == '__main__':
    check_unavailable()
