@echo off
REM Quick test script - activates venv and runs tests
cd /d "%~dp0"
call venv\Scripts\activate.bat
python quick_start.py



