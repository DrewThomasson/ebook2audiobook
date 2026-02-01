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

if exist "%INSTALLED_LOG%" (
	for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
		if /i "%%A"=="Miniforge3" set "REMOVE_CONDA=1"
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
:: REMOVE MINIFORGE (FAST, ATOMIC)
:: ========================================================
if defined REMOVE_CONDA if exist "%CONDA_HOME%" (
	echo %CONDA_HOME%
	rd /s /q "%CONDA_HOME%" >nul 2>&1
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
:: CLEAN REPOSITORY CONTENT
:: - echo only first-level items
:: - delete recursively
:: - continue even if some items are already gone
:: ========================================================
echo Cleaning repository content...

for /f "usebackq delims=" %%N in (`dir /b /a "%REAL_INSTALL_DIR%" 2^>nul`) do (
	if /i not "%%N"=="%SCRIPT_NAME%" (
		echo %%N

		if exist "%REAL_INSTALL_DIR%\%%N\." (
			rd /s /q "%REAL_INSTALL_DIR%\%%N" >nul 2>&1
		) else (
			del /f /q "%REAL_INSTALL_DIR%\%%N" >nul 2>&1
		)
	)
)

if exist "%INSTALLED_LOG%" (
	echo .installed
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