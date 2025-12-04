@echo off
setlocal enabledelayedexpansion

:: ---------------------------------------
:: CONFIG
:: ---------------------------------------
set "APP_NAME=ebook2audiobook"
set "SCRIPT_DIR=%~dp0"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "INSTALLED_LOG=%SCRIPT_DIR%.installed"
set "MINIFORGE_PATH=%USERPROFILE%\Miniforge3"
set "SELF=%~f0"
set "TEMP_UNINSTALL=%TEMP%\%APP_NAME%_uninstall.cmd"
:: ---------------------------------------

:: ---------------------------------------
:: SELF-RELAUNCH FROM TEMP
:: ---------------------------------------
if /i not "%SELF%"=="%TEMP_UNINSTALL%" (
    echo Copying uninstaller to temp and relaunching...
    copy "%SELF%" "%TEMP_UNINSTALL%" >nul
    echo Starting temporary uninstaller...
    start "" cmd /c ""%TEMP_UNINSTALL%" "%SCRIPT_DIR%""
    exit /b
)

:: Now running from TEMP with the original install path
if "%~1"=="" (
    echo [ERROR] Install directory argument missing.
    pause
    exit /b 1
)
set "REAL_INSTALL_DIR=%~1"

echo.
echo ========================================
echo   Uninstalling %APP_NAME%
echo ========================================
echo.

:: ---------------------------------------
:: KILL PROCESSES
:: ---------------------------------------
taskkill /IM "%APP_NAME%.exe" /F >nul 2>&1
taskkill /IM "python.exe" /F >nul 2>&1

:: ---------------------------------------
:: PROCESS .installed PACKAGES
:: ---------------------------------------
set "REMOVE_MINIFORGE="
set "SCOOP_PRESENT="

if exist "%INSTALLED_LOG%" (
    echo Reading .installed list...
    for /f "usebackq delims=" %%A in ("%INSTALLED_LOG%") do (
        set "ITEM=%%A"
        if "!ITEM!"=="" (continue)

        if /i "!ITEM!"=="Miniforge3" (
            set "REMOVE_MINIFORGE=1"
            echo Miniforge3 will be removed manually...
            continue
        )

        if /i "!ITEM!"=="scoop" (
            set "SCOOP_PRESENT=1"
            echo Scoop uninstall will be performed at the very end...
            continue
        )

        echo Uninstalling !ITEM! via Scoop...
        scoop uninstall "!ITEM!" >nul 2>&1
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
    echo Scheduling Scoop removal in background...
    start /b "" cmd /c "ping 127.0.0.1 -n 3 >nul & scoop uninstall scoop >nul 2>&1 & rd /s /q "%USERPROFILE%\scoop" >nul 2>&1"
)

:: ---------------------------------------
:: REMOVE SHORTCUTS AND REGISTRY
:: ---------------------------------------
echo Removing start menu shortcut...
if exist "%STARTMENU_DIR%" rd /s /q "%STARTMENU_DIR%" >nul 2>&1

echo Removing desktop shortcut...
if exist "%DESKTOP_LNK%" del /q "%DESKTOP_LNK%" >nul 2>&1

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\ebook2audiobook" /f >nul 2>&1

:: ---------------------------------------
:: DELETE THE ACTUAL APP FOLDER
:: ---------------------------------------
echo Removing application folder: %REAL_INSTALL_DIR%
rd /s /q "%REAL_INSTALL_DIR%" >nul 2>&1

:: ---------------------------------------
:: CLEAN UP SELF COPY
:: ---------------------------------------
echo.
echo Uninstall complete.
del "%TEMP_UNINSTALL%" >nul 2>&1"
cd ..\

timeout /t 2 >nul
exit /b