$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Starting local reminder app..."

$logPath = Join-Path $scriptDir "launcher.log"
"Starting local reminder app..." | Set-Content -Path $logPath -Encoding UTF8
"Folder: $scriptDir" | Add-Content -Path $logPath -Encoding UTF8
"Date: $(Get-Date)" | Add-Content -Path $logPath -Encoding UTF8

if (Test-Path "F:\anaconda1\python.exe") {
    Write-Host "Using F:\anaconda1\python.exe"
    "Using F:\anaconda1\python.exe" | Add-Content -Path $logPath -Encoding UTF8
    & "F:\anaconda1\python.exe" run_reminder.py *>> $logPath
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Using python from PATH"
    "Using python from PATH" | Add-Content -Path $logPath -Encoding UTF8
    python run_reminder.py
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    Write-Host "Using py launcher"
    "Using py launcher" | Add-Content -Path $logPath -Encoding UTF8
    py -3 run_reminder.py
} else {
    Write-Host "Python was not found. Please install Python 3 first."
    Read-Host "Press Enter to exit"
}

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "The app failed to start or crashed."
    Write-Host "If error.log exists in this folder, send its content to Codex."
    Read-Host "Press Enter to exit"
}
