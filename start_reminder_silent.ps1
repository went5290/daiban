$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$logPath = Join-Path $scriptDir "launcher.log"
"Starting local reminder app silently..." | Set-Content -Path $logPath -Encoding UTF8
"Folder: $scriptDir" | Add-Content -Path $logPath -Encoding UTF8
"Date: $(Get-Date)" | Add-Content -Path $logPath -Encoding UTF8

$pythonwCandidates = @(
    "F:\anaconda1\pythonw.exe",
    "F:\anaconda1\python.exe"
)

$pythonw = $null
foreach ($candidate in $pythonwCandidates) {
    if (Test-Path $candidate) {
        $pythonw = $candidate
        break
    }
}

if (-not $pythonw) {
    $pathPythonw = Get-Command pythonw -ErrorAction SilentlyContinue
    if ($pathPythonw) {
        $pythonw = $pathPythonw.Source
    }
}

if (-not $pythonw) {
    $pathPython = Get-Command python -ErrorAction SilentlyContinue
    if ($pathPython) {
        $pythonw = $pathPython.Source
    }
}

if (-not $pythonw) {
    "Python was not found." | Add-Content -Path $logPath -Encoding UTF8
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show("Python was not found. Please install Python 3 first.", "Local Reminder App")
    exit 1
}

"Using $pythonw" | Add-Content -Path $logPath -Encoding UTF8
Start-Process -FilePath $pythonw -ArgumentList "`"$scriptDir\run_reminder.pyw`"" -WorkingDirectory $scriptDir -WindowStyle Hidden
