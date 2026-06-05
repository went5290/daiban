@echo off
cd /d "%~dp0"

echo Building Daiban Reminder...

if exist "F:\anaconda1\python.exe" (
    set "PYTHON=F:\anaconda1\python.exe"
) else (
    set "PYTHON=python"
)

"%PYTHON%" -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    "%PYTHON%" -m pip install pyinstaller
)

"%PYTHON%" -m PyInstaller ^
    --noconsole ^
    --uac-admin ^
    --onefile ^
    --icon assets\app.ico ^
    --add-data "assets;assets" ^
    --name DaibanReminder ^
    run_reminder.pyw

echo.
echo Build finished. The exe is in the dist folder:
echo dist\DaibanReminder.exe
pause
