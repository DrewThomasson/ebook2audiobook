@echo off

setlocal enabledelayedexpansion

:: ---------------------------------------
:: CONFIG
:: ---------------------------------------
set "APP_NAME=ebook2audiobook"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "INSTALLED_LOG=%SCRIPT_DIR%\.installed"
set "MINIFORGE_PATH=%USERPROFILE%\Miniforge3"
:: ---------------------------------------

echo ========================================================
echo   %APP_NAME%  Uninstaller
echo ========================================================
echo Running from: %SCRIPT_DIR%

set "REAL_INSTALL_DIR=%SCRIPT_DIR%"

echo Press any key to start uninstall (or close this window to cancel).
pause >nul

cd /d "%REAL_INSTALL_DIR%\.."

:: ---------------------------------------
:: KILL PROCESSES (INFORM and TERMINATE)
:: ---------------------------------------
echo Checking for running program instances...

tasklist | find /i "%APP_NAME%.exe" >nul && (
	echo %APP_NAME%.exe is running and will be terminated.
	taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1
)

tasklist | find /i "python.exe" >nul && (
	echo python.exe is active and will be terminated.
	taskkill /IM "python.exe" /F >nul 2>&1
)

:: ---------------------------------------
:: PROCESS .installed PACKAGES
:: ---------------------------------------
set "REMOVE_MINIFORGE="
set "SCOOP_PRESENT="

if exist "%INSTALLED_LOG%" (
	echo Reading .installed packages list...

	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		set "ITEM=%%A"
		if "!ITEM!" NEQ "" (
			if /i "!ITEM!"=="Miniforge3" (
				set "REMOVE_MINIFORGE=1"
				echo Marked Miniforge3 for removal...
			)
			if /i "!ITEM!"=="scoop" (
				set "SCOOP_PRESENT=1"
				echo Scoop presence detected  will remove at end...
			)
			echo Uninstalling package using Scoop: !ITEM!
			call scoop uninstall -y !ITEM! >nul 2>&1
		)
	)
)

:: ---------------------------------------
:: REMOVE MINIFORGE3
:: ---------------------------------------
if defined REMOVE_MINIFORGE (
	if exist "%MINIFORGE_PATH%" (
		echo Removing Miniforge3: %MINIFORGE_PATH%
		rd /s /q "%MINIFORGE_PATH%" >nul 2>&1
	)
)

:: ---------------------------------------
:: DEFERRED SCOOP UNINSTALL
:: ---------------------------------------
if defined SCOOP_PRESENT (
	echo Removing Scoop and cleanup...
	start "" cmd /c "ping 127.0.0.1 -n 3 >nul & scoop uninstall -y scoop >nul 2>&1 & rd /s /q %USERPROFILE%\scoop >nul 2>&1"
)

:: ---------------------------------------
:: REMOVE SHORTCUTS AND REGISTRY
:: ---------------------------------------
echo Removing Menu entries and Desktop shortcuts...

if exist "%STARTMENU_DIR%" rd /s /q "%STARTMENU_DIR%" >nul 2>&1
if exist "%DESKTOP_LNK%" del /q "%DESKTOP_LNK%" >nul 2>&1

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ---------------------------------------
:: DELETE THE ACTUAL APP FOLDER (DEFERRED, VERBOSE)
:: ---------------------------------------
echo Removing application directory:
echo %REAL_INSTALL_DIR%

echo ============================
echo Uninstallation complete.
echo Press any key to close this window.
echo ============================
pause >nul

start "" cmd /c ^
"ping 127.0.0.1 -n 3 >nul ^
& echo. ^
& echo === Removing files and folders === ^
& rd /s "%REAL_INSTALL_DIR%""

exit /b