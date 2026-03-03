import sqlite3
import json

data = [
  {
    "facility": "Main Beach Volleyball Court 01",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 02",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 03",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 04",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 05",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 06",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 07",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 08",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 09",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 10",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 11",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 12",
    "available_slots": ["7:00 am - 8:00 am", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": ["8:00 am - 4:00 pm (Unavailable)"]
  },
  {
    "facility": "Main Beach Volleyball Court 13",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 14",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 15",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 16",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 17",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  },
  {
    "facility": "Main Beach Volleyball Court 18",
    "available_slots": ["7:00 am - 8:00 am", "8:00 am - 9:00 am", "9:00 am - 10:00 am", "10:00 am - 11:00 am", "11:00 am - 12:00 pm", "12:00 pm - 1:00 pm", "1:00 pm - 2:00 pm", "2:00 pm - 3:00 pm", "3:00 pm - 4:00 pm", "4:00 pm - 5:00 pm", "5:00 pm - 6:00 pm", "6:00 pm - 7:00 pm", "7:00 pm - 8:00 pm", "8:00 pm - 9:00 pm", "9:00 pm - 10:00 pm", "10:00 pm - 11:00 pm"],
    "booked_slots": []
  }
]

def insert_data():
    conn = sqlite3.connect('c:/volleyball/volleyball.db')
    c = conn.cursor()
    
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
    
    for court in data:
        c.execute("INSERT OR IGNORE INTO courts (name) VALUES (?)", (court['facility'],))
        c.execute("SELECT id FROM courts WHERE name = ?", (court['facility'],))
        court_id = c.fetchone()[0]
        
        for slot in court['available_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status) VALUES (?, ?, ?)", (court_id, slot, 'available'))
            
        for slot in court['booked_slots']:
            c.execute("INSERT INTO slots (court_id, time_slot, status) VALUES (?, ?, ?)", (court_id, slot, 'unavailable'))
            
    conn.commit()
    conn.close()
    print("Data inserted successfully into volleyball.db")

if __name__ == "__main__":
    insert_data()
