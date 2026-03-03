import sqlite3

conn = sqlite3.connect('volleyball.db')
c = conn.cursor()

c.execute("SELECT name FROM courts")
courts = c.fetchall()

for court in courts:
    court_name = court[0]
    c.execute("SELECT court_id, status, count(*) FROM slots WHERE court_id = (SELECT id FROM courts WHERE name = ?) GROUP BY status", (court_name,))
    slots = c.fetchall()
    print(f"Court: {court_name}")
    for slot in slots:
        print(f"  {slot[1]}: {slot[2]}")

c.execute("SELECT DISTINCT time_slot FROM slots ORDER BY id")
print("Time slots:", c.fetchall())

conn.close()
