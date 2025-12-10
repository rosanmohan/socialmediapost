@echo off
echo Starting Bulletin Scheduler...
echo Press Ctrl+C to stop
call venv\Scripts\activate
python scheduler_bulletin.py
pause
