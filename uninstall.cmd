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
set "HELPER=%TEMP%\%APP_NAME%_uninstall_%RANDOM%.cmd"
set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "CONDA_HOME=%USERPROFILE%\Miniforge3"
set "CONDA_ENV=%CONDA_HOME%\condabin\conda.bat"
set "CONDA_PATH=%CONDA_HOME%\condabin"
:: ========================================================

echo ========================================================
echo   %APP_NAME%  Uninstaller
echo ========================================================
echo Install location:
echo   %REAL_INSTALL_DIR%
echo.

:: ========================================================
:: TERMINATE APP PROCESS ONLY
:: ========================================================
tasklist | find /i "%APP_NAME%.exe" >nul && (
	echo Terminating %APP_NAME%.exe
	taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1
)

:: ========================================================
:: PROCESS .installed (CONTROLLED REMOVAL)
:: ========================================================
set "REMOVE_CONDA="
set "REMOVE_SCOOP="

if exist "%INSTALLED_LOG%" (
	echo Processing installed components...
	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		if /i "%%A"=="Miniforge3" set "REMOVE_CONDA=1"
		if /i "%%A"=="scoop" set "REMOVE_SCOOP=1"
	)
)

:: ========================================================
:: DETACH FROM CONDA ENV (CRITICAL)
:: ========================================================
if defined REMOVE_CONDA (
	echo Detaching from Conda environment...
	set "CONDA_SHLVL="
	set "CONDA_DEFAULT_ENV="
	set "CONDA_PREFIX="
	set "PATH=%SystemRoot%\System32;%SystemRoot%"
)

:: ========================================================
:: REMOVE MINIFORGE (SAFE – CHILD SHELL)
:: ========================================================
if defined REMOVE_CONDA (
	if exist "%CONDA_HOME%" (
		echo Removing Miniforge3 from:
		echo   %CONDA_HOME%
		start "" cmd /c "ping 127.0.0.1 -n 3 >nul & rd /s /q ""%CONDA_HOME%"" >nul 2>&1"
	)
)

:: ========================================================
:: SAFE PATH CLEANUP (DETECTED PATHS ONLY)
:: ========================================================
if defined REMOVE_CONDA (
	call :RemoveFromUserPath "%CONDA_HOME%"
	call :RemoveFromUserPath "%CONDA_PATH%"
)

if defined REMOVE_SCOOP (
	call :RemoveFromUserPath "%SCOOP_SHIMS%"
)

:: ========================================================
:: REMOVE SCOOP LAST (DETECTED LOCATION)
:: ========================================================
if defined REMOVE_SCOOP (
	echo Removing Scoop from:
	echo   %SCOOP_HOME%
	start "" cmd /c "cd /d %%TEMP%% & ping 127.0.0.1 -n 3 >nul & if exist ""%SCOOP_HOME%\shims\scoop.cmd"" ""%SCOOP_HOME%\shims\scoop.cmd"" uninstall -y scoop >nul 2>&1 & rd /s /q ""%SCOOP_HOME%"" >nul 2>&1"
)

:: ========================================================
:: REMOVE SHORTCUTS + REGISTRY
:: ========================================================
if exist "%STARTMENU_DIR%" rd /s /q "%STARTMENU_DIR%" >nul 2>&1
if exist "%DESKTOP_LNK%" del /q "%DESKTOP_LNK%" >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ========================================================
:: FINAL USER MESSAGE
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
	echo setlocal EnableExtensions
	echo set "TARGET=%REAL_INSTALL_DIR%"
	echo cd /d %%TEMP%%
	echo ping 127.0.0.1 -n 6 ^>nul
	echo if exist "%%TARGET%%" attrib -r -s -h "%%TARGET%%" /s /d ^>nul 2^>^&1
	echo if exist "%%TARGET%%" takeown /f "%%TARGET%%" /r /d y ^>nul 2^>^&1
	echo if exist "%%TARGET%%" icacls "%%TARGET%%" /grant *S-1-1-0:F /t ^>nul 2^>^&1
	echo for %%%%I in (1 2 3 4 5) do rd /s /q "%%TARGET%%" ^>nul 2^>^&1
	echo del /f /q "%%~f0"
) > "%HELPER%"

:: ========================================================
:: LAUNCH HELPER AND EXIT
:: ========================================================
start "" /min cmd /c "%HELPER%"
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