import sqlite3
import os
import datetime

def verify_system():
    print("--- System Verification ---")
    
    # 1. Check Database
    db_path = 'c:/volleyball/volleyball.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*) FROM courts")
        court_count = c.fetchone()[0]
        print(f"[DB] Total courts: {court_count}")
        
        c.execute("SELECT status, COUNT(*) FROM slots GROUP BY status")
        slots = c.fetchall()
        for status, count in slots:
            print(f"[DB] {status} slots: {count}")
            
        # Check a sample
        c.execute("SELECT name FROM courts LIMIT 1")
        sample_court = c.fetchone()[0]
        print(f"[DB] Sample court: {sample_court}")
        
        conn.close()
    else:
        print("[ERR] Database not found!")

    # 2. Check Files
    files_to_check = [
        'map_status.png',
        'court_coords.json',
        'vb.bat',
        'auto_scraper.py',
        'generate_map.py',
        'upload_map.py'
    ]
    
    for f in files_to_check:
        path = os.path.join('c:/volleyball/', f)
        if os.path.exists(path):
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(path))
            print(f"[FILE] {f} exists (Last modified: {mtime})")
        else:
            print(f"[ERR] {f} is missing!")

    print("--- Verification Complete ---")

if __name__ == '__main__':
    verify_system()
