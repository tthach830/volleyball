import sqlite3

courts = [f"Main Beach Volleyball Court {i:02d}" for i in range(1, 19)]
all_slots = [
    "7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am",
    "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm",
    "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm",
    "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"
]

def insert_march5():
    conn = sqlite3.connect('c:/volleyball/volleyball.db')
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS slots')
    c.execute('DROP TABLE IF EXISTS courts')
    
    # Create tables
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
            FOREIGN KEY(court_id) REFERENCES courts(id)
        )
    ''')
    
    for court in courts:
        c.execute("INSERT OR IGNORE INTO courts (name) VALUES (?)", (court,))
        c.execute("SELECT id FROM courts WHERE name = ?", (court,))
        court_id = c.fetchone()[0]
        
        court_num = int(court.split()[-1])
        
        for slot in all_slots:
            if 4 <= court_num <= 12 and (slot == "4:00 pm - 5:00 pm" or slot == "5:00 pm - 6:00 pm"):
                status = 'unavailable'
            else:
                status = 'available'
            c.execute("INSERT INTO slots (court_id, time_slot, status) VALUES (?, ?, ?)", (court_id, slot, status))
            
    conn.commit()
    conn.close()
    print("March 5th data inserted successfully.")

if __name__ == '__main__':
    insert_march5()
