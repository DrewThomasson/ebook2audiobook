@echo off
setlocal EnableExtensions EnableDelayedExpansion

:: ========================================================
:: CONFIG
:: ========================================================
set "APP_NAME=ebook2audiobook"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "REAL_INSTALL_DIR=%SCRIPT_DIR%"
set "SCRIPT_NAME=%~nx0"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "INSTALLED_LOG=%SCRIPT_DIR%\.installed"
set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "CONDA_HOME=%USERPROFILE%\Miniforge3"
set "CONDA_PATH=%CONDA_HOME%\condabin"
:: ========================================================

echo ========================================================
echo   %APP_NAME%  Uninstaller
echo ========================================================
echo Install location:
echo   %REAL_INSTALL_DIR%
echo.

:: ========================================================
:: USER CONFIRMATION
:: ========================================================
echo ========================================================
echo   This will uninstall %APP_NAME%.
echo   Components listed in .installed will be removed.
echo.
echo   Press a key to continue . . .
echo ========================================================
pause >nul
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
	echo Processing installed components…
	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		if /i "%%A"=="Miniforge3" set "REMOVE_CONDA=1"
		if /i "%%A"=="scoop" set "REMOVE_SCOOP=1"
	)
)

:: ========================================================
:: DETACH FROM CONDA (SAFETY)
:: ========================================================
if defined REMOVE_CONDA (
	set "CONDA_SHLVL="
	set "CONDA_DEFAULT_ENV="
	set "CONDA_PREFIX="
	set "PATH=%SystemRoot%\System32;%SystemRoot%"
)

:: ========================================================
:: REMOVE MINIFORGE (DIRECT)
:: ========================================================
if defined REMOVE_CONDA if exist "%CONDA_HOME%" (
	echo %CONDA_HOME%
	rd /s /q "%CONDA_HOME%" >nul 2>&1
)

:: ========================================================
:: REMOVE SCOOP (DIRECT)
:: ========================================================
if defined REMOVE_SCOOP if exist "%SCOOP_HOME%" (
	echo %SCOOP_HOME%
	rd /s /q "%SCOOP_HOME%" >nul 2>&1
)

:: ========================================================
:: CLEAN USER PATH (ONLY KNOWN ENTRIES)
:: ========================================================
if defined REMOVE_CONDA (
	call :RemoveFromUserPath "%CONDA_HOME%"
	call :RemoveFromUserPath "%CONDA_PATH%"
)

if defined REMOVE_SCOOP (
	call :RemoveFromUserPath "%SCOOP_SHIMS%"
)

:: ========================================================
:: REMOVE SHORTCUTS + REGISTRY
:: ========================================================
if exist "%STARTMENU_DIR%" (
	echo %STARTMENU_DIR%
	rd /s /q "%STARTMENU_DIR%" >nul 2>&1
)

if exist "%DESKTOP_LNK%" (
	echo %DESKTOP_LNK%
	del /q "%DESKTOP_LNK%" >nul 2>&1
)

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ========================================================
:: REMOVE CURRENT REPO CONTENT (RECURSIVE, VERBOSE)
:: ========================================================
echo Cleaning repository content...

:: --- fast delete heavy directories (no listing) ---
if exist "%REAL_INSTALL_DIR%\%SKIP_DIR_1%" (
	echo %REAL_INSTALL_DIR%\%SKIP_DIR_1%
	rd /s /q "%REAL_INSTALL_DIR%\%SKIP_DIR_1%" >nul 2>&1
)

:: --- remove files first (skip uninstaller + skipped dirs) ---
for /r "%REAL_INSTALL_DIR%" %%F in (*) do (
	set "P=%%~dpF"
	set "N=%%~nxF"

	echo !P! | findstr /i "\\%SKIP_DIR_1%\\" >nul && goto :next_file

	if /i not "!N!"=="%SCRIPT_NAME%" (
		echo %%F
		del /f /q "%%F" >nul 2>&1
	)

	:next_file
)

for /f "delims=" %%D in ('dir "%REAL_INSTALL_DIR%" /ad /b /s ^| sort /r') do (
	echo %%D | findstr /i "\\%SKIP_DIR_1%$" >nul && goto :next_dir
	echo %%D | findstr /i "\\%SKIP_DIR_1%\\" >nul && goto :next_dir

	echo %%D
	rd "%%D" >nul 2>&1

	:next_dir
)

if exist "%INSTALLED_LOG%" (
	echo %INSTALLED_LOG%
	del /f /q "%INSTALLED_LOG%" >nul 2>&1
)

:: ========================================================
:: FINAL MESSAGE
:: ========================================================
echo.
echo ========================================================
echo   Uninstallation completed.
echo.
echo   The application content has been removed.
echo   Please remove the empty repository folder manually:
echo.
echo     %REAL_INSTALL_DIR%
echo.
echo ========================================================
echo.
echo Press a key to continue . . .
pause >nul

exit /b

:: ========================================================
:: FUNCTIONS
:: ========================================================
:RemoveFromUserPath
echo Removing from PATH: %~1
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