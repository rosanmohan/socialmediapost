@echo off
REM Quick run script - activates venv and runs the agent
cd /d "%~dp0"
call venv\Scripts\activate.bat
python main.py %*



