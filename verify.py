import sqlite3

def verify():
    conn = sqlite3.connect('c:/volleyball/volleyball.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM courts")
    courts_count = c.fetchone()[0]
    print(f"Total courts: {courts_count}")
    
    c.execute("SELECT status, COUNT(*) FROM slots GROUP BY status")
    slots_count = c.fetchall()
    for row in slots_count:
        print(f"Total {row[0]} slots: {row[1]}")
        
if __name__ == "__main__":
    verify()
