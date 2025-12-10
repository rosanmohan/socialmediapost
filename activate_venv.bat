@echo off
REM Activate virtual environment and run command
cd /d "%~dp0"
call venv\Scripts\activate.bat
if "%1"=="" (
    echo Virtual environment activated!
    echo.
    echo Available commands:
    echo   python quick_start.py          - Test all components
    echo   python main.py --mode run      - Run once
    echo   python main.py --mode schedule - Start 24/7 scheduler
    echo.
    cmd /k
) else (
    %*
)



