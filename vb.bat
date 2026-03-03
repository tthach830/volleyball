@echo off
cd /d c:\volleyball
echo Starting Volleyball Automation...
.venv\Scripts\python.exe auto_scraper.py %1
.venv\Scripts\python.exe generate_map.py
.venv\Scripts\python.exe upload_map.py
echo All tasks complete!
