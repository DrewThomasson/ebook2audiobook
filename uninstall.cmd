@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ========================================================
:: CONFIG
:: ========================================================
set "APP_NAME=ebook2audiobook"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "REAL_INSTALL_DIR=%SCRIPT_DIR%"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "INSTALLED_LOG=%SCRIPT_DIR%\.installed"
set "MINIFORGE_PATH=%USERPROFILE%\Miniforge3"
set "SCOOP_PATH=%USERPROFILE%\scoop"
set "HELPER=%TEMP%\%APP_NAME%_uninstall_helper.cmd"
:: ========================================================

echo ========================================================
echo   %APP_NAME%  Uninstaller
echo ========================================================
echo Install location:
echo   %REAL_INSTALL_DIR%
echo.

pause

:: ========================================================
:: TERMINATE APP PROCESS ONLY
:: ========================================================
tasklist | find /i "%APP_NAME%.exe" >nul && (
	echo Terminating %APP_NAME%.exe
	taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1
)

:: ========================================================
:: PROCESS .installed (SCOOP PACKAGES)
:: ========================================================
set "REMOVE_MINIFORGE="
set "SCOOP_PRESENT="

if exist "%INSTALLED_LOG%" (
	echo Processing installed packages...
	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		if /i "%%A"=="Miniforge3" set "REMOVE_MINIFORGE=1"
		if /i "%%A"=="scoop" set "SCOOP_PRESENT=1"
		call scoop uninstall -y %%A >nul 2>&1
	)
)

:: ========================================================
:: REMOVE MINIFORGE
:: ========================================================
if defined REMOVE_MINIFORGE (
	if exist "%MINIFORGE_PATH%" (
		echo Removing Miniforge3...
		rd /s /q "%MINIFORGE_PATH%" >nul 2>&1
	)
)

:: ========================================================
:: SAFE PATH CLEANUP (HKCU ONLY)
:: ========================================================
call :RemoveFromUserPath "%MINIFORGE_PATH%"
call :RemoveFromUserPath "%MINIFORGE_PATH%\Scripts"
call :RemoveFromUserPath "%SCOOP_PATH%\shims"

:: ========================================================
:: REMOVE SCOOP LAST (DEFERRED)
:: ========================================================
if defined SCOOP_PRESENT (
	echo Removing Scoop...
	start "" cmd /c ^
	"ping 127.0.0.1 -n 3 >nul ^
	& scoop uninstall -y scoop >nul 2>&1 ^
	& rd /s /q "%SCOOP_PATH%" >nul 2>&1"
)

:: ========================================================
:: REMOVE SHORTCUTS + REGISTRY
:: ========================================================
if exist "%STARTMENU_DIR%" rd /s /q "%STARTMENU_DIR%" >nul 2>&1
if exist "%DESKTOP_LNK%" del /q "%DESKTOP_LNK%" >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ========================================================
:: FINAL USER MESSAGE (OPTION B)
:: ========================================================
echo.
echo ========================================================
echo   Uninstallation completed successfully.
echo   Cleaning up remaining files in background...
echo   This window will close automatically.
echo ========================================================
echo.
timeout /t 4 >nul

:: ========================================================
:: CREATE SELF-DELETING HELPER
:: ========================================================
(
	echo @echo off
	echo ping 127.0.0.1 -n 5 ^>nul
	echo rd /s /q "%REAL_INSTALL_DIR%" ^>nul 2^>^&1
	echo del /f /q "%%~f0"
) > "%HELPER%"

:: ========================================================
:: LAUNCH HELPER AND EXIT
:: ========================================================
start "" "%HELPER%"
exit /b

:: ========================================================
:: FUNCTIONS
:: ========================================================
:RemoveFromUserPath
set "TARGET=%~1"
for /f "tokens=2,*" %%A in ('reg query HKCU\Environment /v PATH 2^>nul ^| find "PATH"') do set "USERPATH=%%B"
set "NEWPATH="
for %%P in (!USERPATH:;=^
!) do (
	if /i not "%%P"=="%TARGET%" (
		if defined NEWPATH (
			set "NEWPATH=!NEWPATH!;%%P"
		) else (
			set "NEWPATH=%%P"
		)
	)
)
reg add HKCU\Environment /v PATH /t REG_EXPAND_SZ /d "!NEWPATH!" /f >nul
exit /b