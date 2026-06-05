Set shell = CreateObject("Shell.Application")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptPath = WScript.ScriptFullName
scriptDir = fso.GetParentFolderName(scriptPath)
psPath = fso.BuildPath(scriptDir, "start_reminder_silent.ps1")

shell.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File """ & psPath & """", scriptDir, "runas", 0
