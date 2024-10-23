@echo off
:: Check for administrative privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script requires administrator privileges.
    echo Switching to administrator...

    powershell -Command "Start-Process cmd -ArgumentList '/c', '%~dpnx0' -Verb runAs"
    exit /b
)

:: If already elevated, continue the script
echo Running with administrator privileges...

:: Run the PowerShell script in the same directory as this batch file
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"

pause
