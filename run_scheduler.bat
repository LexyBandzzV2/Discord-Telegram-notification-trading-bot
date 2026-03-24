@echo off
REM Trading Bot Scheduler Launcher
REM Runs the trading bot scheduler in the background

echo.
echo ===============================================================================
echo   TRADING BOT SCHEDULER LAUNCHER
echo ===============================================================================
echo.

REM Get the script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found. Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment and start scheduler
echo Starting Trading Bot Scheduler...
echo Time: 9:00 AM EST (Weekdays)
echo.

call .venv\Scripts\activate.bat
python scheduler.py

pause
