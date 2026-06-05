@echo off
net session >nul 2>&1
if not "%errorlevel%"=="0" (
    echo Requesting administrator permission...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo Starting local reminder app...
echo Starting local reminder app... > launcher.log
echo Folder: %CD% >> launcher.log
echo Date: %DATE% %TIME% >> launcher.log

if exist "F:\anaconda1\python.exe" (
    echo Using F:\anaconda1\python.exe
    echo Using F:\anaconda1\python.exe >> launcher.log
    "F:\anaconda1\python.exe" run_reminder.py >> launcher.log 2>&1
) else (
    where python >> launcher.log 2>&1
    where python >nul 2>nul
    if %errorlevel%==0 (
        echo Using python from PATH
        echo Using python from PATH >> launcher.log
        python run_reminder.py >> launcher.log 2>&1
    ) else (
        echo Using py launcher
        echo Using py launcher >> launcher.log
        py -3 run_reminder.py >> launcher.log 2>&1
    )
)

if errorlevel 1 (
    echo.
    echo The app failed to start or crashed.
    echo See launcher.log and error.log in this folder.
    echo.
    pause
) else (
    echo App closed normally. >> launcher.log
)
