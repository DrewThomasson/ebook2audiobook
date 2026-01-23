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

echo.
echo ========================================================
echo   %APP_NAME% — Uninstaller
echo ========================================================
echo Running from: %SCRIPT_DIR%
echo.

set "REAL_INSTALL_DIR=%SCRIPT_DIR%"

choice /M "Proceed with uninstall?" /C YN
if errorlevel 2 exit /b

cd /d "%REAL_INSTALL_DIR%\.."

:: ---------------------------------------
:: KILL PROCESSES (POLITE FIRST)
:: ---------------------------------------
echo.
echo Checking for running program instances...

tasklist | find /i "%APP_NAME%.exe" >nul && (
	echo %APP_NAME%.exe is currently running.
	choice /M "Terminate it to continue?" /C YN
	if errorlevel 1 taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1
)

tasklist | find /i "python.exe" >nul && (
	echo Python is active and may be linked to the app.
	choice /M "Close python.exe automatically?" /C YN
	if errorlevel 1 taskkill /IM "python.exe" /F >nul 2>&1
)

:: ---------------------------------------
:: PROCESS .installed PACKAGES
:: ---------------------------------------
set "REMOVE_MINIFORGE="
set "SCOOP_PRESENT="

if exist "%INSTALLED_LOG%" (
	echo.
	echo Reading .installed packages list...

	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		set "ITEM=%%A"

		if not defined ITEM (
			rem skip empty line
		) else if /i "!ITEM!"=="Miniforge3" (
			set "REMOVE_MINIFORGE=1"
			echo Marked Miniforge3 for removal...
		) else if /i "!ITEM!"=="scoop" (
			set "SCOOP_PRESENT=1"
			echo Scoop presence detected — will remove at end...
		) else (
			echo Uninstalling package using Scoop: !ITEM!
			scoop uninstall "!ITEM!" >nul 2>&1
		)
	)
)

:: ---------------------------------------
:: REMOVE MINIFORGE3
:: ---------------------------------------
if defined REMOVE_MINIFORGE (
	if exist "%MINIFORGE_PATH%" (
		echo.
		echo Removing Miniforge3: %MINIFORGE_PATH%
		rd /s /q "%MINIFORGE_PATH%" >nul 2>&1
	)
)

:: ---------------------------------------
:: DEFERRED SCOOP UNINSTALL
:: ---------------------------------------
if defined SCOOP_PRESENT (
	echo.
	echo Removing Scoop and cleanup...
	start "" cmd /c ^
	"ping 127.0.0.1 -n 3 >nul ^
	& scoop uninstall scoop >nul 2>&1 ^
	& rd /s /q "%USERPROFILE%\scoop" >nul 2>&1"
)

:: ---------------------------------------
:: REMOVE SHORTCUTS AND REGISTRY
:: ---------------------------------------
echo.
echo Removing Menu entries & Desktop shortcuts...

if exist "%STARTMENU_DIR%" rd /s /q "%STARTMENU_DIR%" >nul 2>&1
if exist "%DESKTOP_LNK%" del /q "%DESKTOP_LNK%" >nul 2>&1

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ---------------------------------------
:: DELETE THE ACTUAL APP FOLDER (DEFERRED)
:: ---------------------------------------
echo.
echo Scheduling final application directory removal:
echo %REAL_INSTALL_DIR%

start "" cmd /c ^
"ping 127.0.0.1 -n 3 >nul ^
& rd /s /q "%REAL_INSTALL_DIR%" >nul 2>&1"

echo.
echo ============================
echo Uninstallation complete.
echo ============================

timeout /t 2 >nul
exit /b