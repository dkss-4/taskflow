@echo off
@echo off
echo Running TaskFlow Reminders...
echo.

REM Navigate to your project directory
cd /d E:\backend_project\taskflow

REM Check if virtual environment exists
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
    echo Virtual environment activated
) else (
    echo ERROR: Virtual environment not found at venv\
    pause
    exit /b 1
)

REM Run the reminder command
python manage.py send_reminders

REM Keep window open to see results
echo.
echo Done! Press any key to close...
pause > nul