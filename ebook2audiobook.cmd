@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "SAFE_USERPROFILE=%USERPROFILE%"
set "SAFE_SCRIPT_DIR=%~dp0"
if "%SAFE_SCRIPT_DIR:~-1%"=="\" set "SAFE_SCRIPT_DIR=%SAFE_SCRIPT_DIR:~0,-1%"

:: Force UTF-8 for CMD
chcp 65001 >nul

:: Prefer PowerShell 7, fallback to Windows PowerShell 5.1
set "PS_EXE=pwsh"
where.exe /Q pwsh >nul 2>&1 || set "PS_EXE=powershell"

:: One canonical set of flags for every PowerShell call in this script
set "PS_ARGS=-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass"

:: Detect Constrained Language Mode (corporate lockdown)
"%PS_EXE%" %PS_ARGS% -Command "if ($ExecutionContext.SessionState.LanguageMode -ne 'FullLanguage') { exit 99 }"
if errorlevel 99 (
    echo ERROR: PowerShell Constrained Language Mode detected. This environment is not supported.
    goto :failed
)

:: Ensure PS output encoding is UTF-8 for this session (non-persistent)
"%PS_EXE%" %PS_ARGS% -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8" >nul 2>&1

:: Enable ANSI VT mode
reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if errorlevel 1 (
    reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
)

:: Real ESC byte via PowerShell (RELIABLE)
for /f "delims=" %%e in ('
    cmd /c ""%PS_EXE%" %PS_ARGS% -Command "[char]27""
') do set "ESC=%%e"

:: Capture all arguments into ARGS
set "ARGS=%*"
set "NATIVE=native"
set "BUILD_DOCKER=build_docker"
set "FULL_DOCKER=full_docker"
set "SCRIPT_MODE=%NATIVE%"
set "APP_NAME=ebook2audiobook"
set /p APP_VERSION=<"%SAFE_SCRIPT_DIR%\VERSION.txt"
set "APP_FILE=%APP_NAME%.cmd"
set "OS_LANG="
for /f "skip=1 tokens=3" %%A in ('reg query "HKCU\Control Panel\International" /v LocaleName 2^>nul') do set "OS_LANG=%%A"
if defined OS_LANG set "OS_LANG=%OS_LANG:~0,2%"
if not defined OS_LANG set "OS_LANG=en"
set "TEST_HOST=127.0.0.1"
set "TEST_PORT=7860"
set "ICON_PATH=%SAFE_SCRIPT_DIR%\tools\icons\windows\appIcon.ico"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "STARTMENU_LNK=%STARTMENU_DIR%\%APP_NAME%.lnk"
set "DESKTOP_LNK=%SAFE_USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "ARCH=%PROCESSOR_ARCHITECTURE%" & if defined PROCESSOR_ARCHITEW6432 set "ARCH=%PROCESSOR_ARCHITEW6432%"
if /i "%ARCH%"=="ARM64" (set "PYTHON_ARCH=arm64") else if /i "%ARCH%"=="AMD64" (set "PYTHON_ARCH=amd64")
set "MIN_PYTHON_VERSION=3.10"
set "MAX_PYTHON_VERSION=3.12"
set "PYTHON_VERSION=3.12"
set "PYTHON_SCOOP=python%PYTHON_VERSION:.=%"
set "PYTHON_ENV=python_env"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="
set "HOST_PROGRAMS=cmake rustup calibre ffmpeg-shared mediainfo nodejs espeak-ng sox tesseract"
:: tesseract-ocr-[lang] and calibre are hardcoded in Dockerfile
set "DOCKER_PROGRAMS=curl ffmpeg mediainfo nodejs espeak-ng sox tesseract-ocr"
set "DOCKER_CALIBRE_INSTALLER_URL=https://download.calibre-ebook.com/linux-installer.sh"
set "DOCKER_WSL_CONTAINER=Debian"
set "DOCKER_FIX_SCRIPT=dpf.ps1"
set "DOCKER_MODE="
set "DOCKER_IMG_NAME=athomasson2/%APP_NAME%"
set "DOCKER_DEVICE_STR="
set "DEVICE_INFO_STR="
set "TMP=%SAFE_SCRIPT_DIR%\run"
set "TEMP=%SAFE_SCRIPT_DIR%\run"
if not exist "%TMP%" mkdir "%TMP%" >nul 2>&1
set "CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
set "CONDA_INSTALLER=Miniforge3-Windows-x86_64.exe"
set "SCOOP_HOME=%SAFE_USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "CONDA_HOME=%SAFE_USERPROFILE%\Miniforge3"
set "CONDA_ENV=%CONDA_HOME%\condabin\conda.bat"
set "CONDA_PATH=%CONDA_HOME%\condabin"
set "ESPEAK_DATA_PATH=%SCOOP_HOME%\apps\espeak-ng\current\eSpeak NG\espeak-ng-data"
set "NODE_PATH=%SCOOP_HOME%\apps\nodejs\current"
set "TESSDATA_PREFIX=%SAFE_SCRIPT_DIR%\models\tessdata"
set "TESSDATA_BASE_URL=https://github.com/tesseract-ocr/tessdata_best/raw/main"
set "FFMPEG_BIN=%USERPROFILE%\scoop\apps\ffmpeg-shared\current\bin"
set "FFMPEG_VARIANT=none"
set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%NODE_PATH%;%FFMPEG_BIN%;%PATH%"
set "INSTALLED_LOG=%SAFE_SCRIPT_DIR%\.installed"
set "UNINSTALLER=%SAFE_SCRIPT_DIR%\uninstall.cmd"
set "BROWSER_HELPER=%SAFE_SCRIPT_DIR%\.bh.ps1"
set "HEADLESS_FOUND=%ARGS:--headless=%"
set "WSL_VERSION="
set "DOCKER_IN_WSL=0"
set "DOCKER_DESKTOP=0"
set "PODMAN_DESKTOP=0"

IF NOT DEFINED DEVICE_TAG SET "DEVICE_TAG="

set "missing_prog_array="

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "PATH=%%B;%PATH%"
)

if "%ARCH%"=="X86" (
    echo %ESC%[31m=============== Error: 32-bit architecture is not supported.%ESC%[0m
    goto :failed
)

if not exist "%INSTALLED_LOG%" if /i not "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
    type nul > "%INSTALLED_LOG%"
)

cd /d "%SAFE_SCRIPT_DIR%"

:: Clear previous associative values
for /f "tokens=1* delims==" %%A in ('set arguments. 2^>nul') do set "%%A="

::::::::::::::::::::::::::::::: CORE FUNCTIONS

if not "%~1"=="" (
    setlocal EnableDelayedExpansion
    for /f "delims=" %%V in ('python -c "from lib.conf import cli_options; print(' '.join(cli_options))"') do set "VALID_ARGS=%%V"
    for %%A in (%*) do (
        set "ARG=%%~A"
        if "!ARG:~0,2!"=="--" (
            set "FOUND=0"
            for %%V in (!VALID_ARGS!) do (
                if /i "!ARG!"=="%%V" set "FOUND=1"
            )
            if !FOUND! equ 0 (
                echo ERROR: Unknown option "!ARG!"
                exit /b 1
            )
        )
    )
    endlocal
)

:parse_args
setlocal EnableDelayedExpansion
if "%~1"=="" goto :parse_args_done
set "arg=%~1"
if "!arg:~0,2!"=="--" (
    set "key=!arg:~2!"
    if not "%~2"=="" (
        echo %~2 | findstr "^--" >nul
        if errorlevel 1 (
            set "arguments.!key!=%~2"
            shift
            shift
            goto parse_args
        )
    )
    set "arguments.!key!=true"
    shift
    goto parse_args
)
shift
goto parse_args


:parse_args_done
endlocal & (
    for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do set "%%A=%%B"
)
if defined arguments.script_mode (
    set "script_mode_valid=0"
    if /i "%arguments.script_mode%"=="%BUILD_DOCKER%" set "script_mode_valid=1"
    if /i "%arguments.script_mode%"=="%FULL_DOCKER%" set "script_mode_valid=1"
)

if defined arguments.script_mode if "%script_mode_valid%"=="1" (
    set "SCRIPT_MODE=%arguments.script_mode%"
)
if defined arguments.script_mode if "%script_mode_valid%"=="0" (
    echo Error: Invalid script mode argument: %arguments.script_mode%
    goto :failed
)
if defined arguments.docker_device (
    if /i "%arguments.docker_device%"=="true" (
        echo Error: --docker_device has no value
        goto :failed
    )
	set "DOCKER_DEVICE_STR=%arguments.docker_device%"
)
if defined arguments.docker_mode (
    if not "%arguments.docker_mode%"=="podman" (
		if not "%arguments.docker_mode%"=="compose" (
			if /i "%arguments.docker_mode%"=="true" (
				echo Error: --docker_mode has no value
			) else (
				echo Error: --docker_mode accepts only podman or compose as value
			)
			goto :failed
		)
    )
	set "DOCKER_MODE=%arguments.docker_mode%"
)
if defined arguments.script_mode (
    if /i "%arguments.script_mode%"=="true" (
        echo Error: --script_mode requires a value
        goto :failed
    )
    if /i not "%arguments.script_mode%"=="FULL_DOCKER" (
        setlocal enabledelayedexpansion
        for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do (
            set "argname=%%A"
            set "argname=!argname:arguments.=!"
            if not "!argname!"=="" (
                if /i not "!argname!"=="script_mode" (
                    if /i not "!argname!"=="docker_device" (
                        if /i not "!argname!"=="docker_mode" (
                            echo Error: when --script_mode is not FULL_DOCKER, only --docker_device or --docker_mode are allowed. Invalid: --!argname!
                            goto :failed
                        )
                    )
                )
            )
        )
        endlocal
    )
)
if defined arguments.version (
	echo v%APP_VERSION%
	goto :eof
)
goto :main

::::::::::::::: DESKTOP APP
:make_shortcut
set "shortcut=%~1"
"%PS_EXE%" %PS_ARGS% -Command "$s=New-Object -ComObject WScript.Shell; $sc=$s.CreateShortcut('%shortcut%'); $sc.TargetPath='cmd.exe'; $sc.Arguments='/k ""cd /d """"%SAFE_SCRIPT_DIR%"""" && """"%APP_FILE%""""""'; $sc.WorkingDirectory='%SAFE_SCRIPT_DIR%'; $sc.IconLocation='%ICON_PATH%'; $sc.Save()"
exit /b

:build_gui
if /i not "%HEADLESS_FOUND%"=="%ARGS%" (
    if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
    if not exist "%STARTMENU_LNK%" (
        call :make_shortcut "%STARTMENU_LNK%"
        call :make_shortcut "%DESKTOP_LNK%"
    )
    for /f "skip=1 delims=" %%L in ('tasklist /v /fo csv /fi "imagename eq powershell.exe" 2^>nul') do (
        echo %%L | findstr /i "%APP_NAME%" >nul && (
            for /f "tokens=2 delims=," %%A in ("%%L") do (
                taskkill /PID %%~A /F >nul 2>&1
            )
        )
    )
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayName" /d "%APP_NAME%" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayVersion" /d "%APP_VERSION%" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "Publisher" /d "ebook2audiobook Team" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "InstallLocation" /d "%SAFE_SCRIPT_DIR%" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "UninstallString" /d "\"%UNINSTALLER%\"" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayIcon" /d "%ICON_PATH%" /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "NoModify" /t REG_DWORD /d 1 /f >nul 2>&1
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "NoRepair" /t REG_DWORD /d 1 /f >nul 2>&1
    start "%APP_NAME%" /min "%PS_EXE%" %PS_ARGS% -File "%BROWSER_HELPER%" -HostName "%TEST_HOST%" -Port %TEST_PORT%
)
exit /b 0
:::::: END OF DESKTOP APP

:get_iso3_lang
set "ISO3_LANG=eng"
if /i "%~1"=="en" set "ISO3_LANG=eng"
if /i "%~1"=="fr" set "ISO3_LANG=fra"
if /i "%~1"=="de" set "ISO3_LANG=deu"
if /i "%~1"=="it" set "ISO3_LANG=ita"
if /i "%~1"=="es" set "ISO3_LANG=spa"
if /i "%~1"=="pt" set "ISO3_LANG=por"
if /i "%~1"=="ar" set "ISO3_LANG=ara"
if /i "%~1"=="tr" set "ISO3_LANG=tur"
if /i "%~1"=="ru" set "ISO3_LANG=rus"
if /i "%~1"=="bn" set "ISO3_LANG=ben"
if /i "%~1"=="zh" set "ISO3_LANG=chi_sim"
if /i "%~1"=="fa" set "ISO3_LANG=fas"
if /i "%~1"=="hi" set "ISO3_LANG=hin"
if /i "%~1"=="hu" set "ISO3_LANG=hun"
if /i "%~1"=="id" set "ISO3_LANG=ind"
if /i "%~1"=="jv" set "ISO3_LANG=jav"
if /i "%~1"=="ja" set "ISO3_LANG=jpn"
if /i "%~1"=="ko" set "ISO3_LANG=kor"
if /i "%~1"=="pl" set "ISO3_LANG=pol"
if /i "%~1"=="ta" set "ISO3_LANG=tam"
if /i "%~1"=="te" set "ISO3_LANG=tel"
if /i "%~1"=="yo" set "ISO3_LANG=yor"
exit /b

:check_python
where.exe python >nul 2>&1
if errorlevel 1 (
	echo Python is not installed.
	exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "INSTALLED_VERSION=%%v"
for /f "tokens=1-3 delims=." %%a in ("%INSTALLED_VERSION%") do (
	set "INS_MAJOR=%%a"
	set "INS_MINOR=%%b"
	set "INS_PATCH=0"
)
for /f "tokens=1-3 delims=." %%a in ("%MIN_PYTHON_VERSION%") do (
	set "REQ_MAJOR=%%a"
	set "REQ_MINOR=%%b"
	set "REQ_PATCH=0"
)
set "PYTHON_OK=1"
if %INS_MAJOR% lss %REQ_MAJOR% set "PYTHON_OK=0"
if %INS_MAJOR% equ %REQ_MAJOR% if %INS_MINOR% lss %REQ_MINOR% set "PYTHON_OK=0"
if %INS_MAJOR% equ %REQ_MAJOR% if %INS_MINOR% equ %REQ_MINOR% if %INS_PATCH% lss %REQ_PATCH% set "PYTHON_OK=0"
if "%PYTHON_OK%"=="0" (
	echo Python %INSTALLED_VERSION% found but %MIN_PYTHON_VERSION% or higher is required.
	exit /b 1
)
exit /b 0

:check_scoop
where.exe /Q scoop >nul 2>&1
if errorlevel 1 (
    echo Scoop is not installed.
    exit /b 1
)
exit /b 0

:check_scoop_buckets
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket list" > "%TEMP%\scoop_buckets.txt" 2>&1
set "_MISSING_BUCKETS="
findstr /i "muggle" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! muggle"
findstr /i "extras" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! extras"
findstr /i "versions" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! versions"
del "%TEMP%\scoop_buckets.txt" >nul 2>&1
if defined _MISSING_BUCKETS (
    exit /b 1
)
exit /b 0

:check_programs
setlocal EnableDelayedExpansion
for %%p in (%HOST_PROGRAMS%) do (
    set "prog=%%p"
    set "_found=0"
    if "%%p"=="nodejs"  set "prog=node"
    if "%%p"=="calibre" set "prog=ebook-convert"
    if "%%p"=="ffmpeg-shared" set "prog=ffmpeg"
    if "%%p"=="rustup" (
        if exist "%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin\rustup.exe" set "_found=1"
    )
    if "!_found!"=="0" (
        where.exe /Q !prog! >nul 2>&1
        if errorlevel 1 (
			set "missing_prog_array=!missing_prog_array! %%p"
		) else (
			if "%%p"=="ffmpeg-shared" (
				call :check_ffmpeg_shared
			)
		)
    )
)
endlocal & set "missing_prog_array=%missing_prog_array%"
if not "%missing_prog_array%"=="" exit /b 1
exit /b 0

:check_ffmpeg_shared
setlocal
set "ffmpeg_pkg=none"
set "tmp_file=%INSTALLED_LOG%.tmp"
if exist "%SCOOP_HOME%\apps\ffmpeg-shared\current\bin\avcodec-*.dll" (
    set "ffmpeg_pkg=shared"
) else if exist "%SCOOP_HOME%\apps\ffmpeg\current\bin\ffmpeg.exe" (
    set "ffmpeg_pkg=static"
) else (
	exit /b 0
)
if "%ffmpeg_pkg%"=="static" (
	echo Static ffmpeg detected, swapping to ffmpeg-shared…
	call scoop uninstall ffmpeg || (echo [xx] uninstall failed & exit /b 1)
	call scoop install ffmpeg-shared || (echo [xx] install failed & exit /b 1)
 	if exist "%INSTALLED_LOG%" (
 		findstr /v /x /c:"ffmpeg" "%INSTALLED_LOG%" > "%tmp_file%" 2>nul
 	) else (
 		type nul > "%tmp_file%"
 	)
	>>"%tmp_file%" echo ffmpeg-shared
	move /y "%tmp_file%" "%INSTALLED_LOG%" >nul
	echo swap complete, .installed updated.
)
endlocal
exit /b 0

:install_python
echo Installing Python %PYTHON_VERSION%…
set "PYTHON_INSTALLER=python-%PYTHON_VERSION%-%PYTHON_ARCH%.exe"
set "PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%.0/python-%PYTHON_VERSION%.0-%PYTHON_ARCH%.exe"
echo Downloading Python installer for %PYTHON_ARCH%…
powershell -NoProfile -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%TEMP%\%PYTHON_INSTALLER%'"
if errorlevel 1 (
    echo %ESC%[31m=============== Failed to download Python installer.%ESC%[0m
    goto :failed
)
echo Installing Python silently…
"%TEMP%\%PYTHON_INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
if errorlevel 1 (
    echo %ESC%[31m=============== Python installation failed.%ESC%[0m
    del "%TEMP%\%PYTHON_INSTALLER%"
    goto :failed
)
del "%TEMP%\%PYTHON_INSTALLER%"
del "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe"
del "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python3.exe"
echo %ESC%[33m=============== Python OK ===============%ESC%[0m
goto :restart_script

:install_scoop
echo Installing Scoop…
call "%PS_EXE%" %PS_ARGS% -Command "irm get.scoop.sh -OutFile '%TEMP%\install_scoop.ps1'"
call "%PS_EXE%" %PS_ARGS% -File "%TEMP%\install_scoop.ps1" -RunAsAdmin
del "%TEMP%\install_scoop.ps1" >nul 2>&1
if errorlevel 1 (
    net session >nul 2>&1
    if not errorlevel 1 (
        goto :restart_script
    )
    goto :failed
)
findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
if errorlevel 1 echo scoop>>"%INSTALLED_LOG%"
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git"
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add extras"
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add versions"
echo %ESC%[33m=============== Scoop OK ===============%ESC%[0m
type nul > "%SAFE_SCRIPT_DIR%\.after-scoop"
goto :restart_script

:install_scoop_buckets
call "%PS_EXE%" %PS_ARGS% -Command "$WarningPreference='SilentlyContinue'; scoop install git; scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git; scoop bucket add extras; scoop bucket add versions"
call git config --global credential.helper
del "%SAFE_SCRIPT_DIR%\.after-scoop" >nul 2>&1
echo %ESC%[32m=============== Scoop components OK ===============%ESC%[0m
exit /b 0

:install_wsl
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	echo WSL2 is required to build Linux containers.
	echo.
	echo ==================================================
	echo WSL and %DOCKER_WSL_CONTAINER% will now be installed.
	echo ==================================================
	pause
	wsl --unregister %DOCKER_WSL_CONTAINER% >nul 2>&1
	wsl --update
	wsl --install -d %DOCKER_WSL_CONTAINER% --no-launch
	echo.
	echo %DOCKER_WSL_CONTAINER% setup complete. Configuring for Docker...
	wsl --shutdown
	timeout /t 3 /nobreak >nul
	wsl --user root -- echo "%DOCKER_WSL_CONTAINER% OK" >nul 2>&1
	if errorlevel 1 (
		echo %ESC%[31m=============== %DOCKER_WSL_CONTAINER% installation failed.%ESC%[0m
		goto :failed
	)
	for /f %%A in ('powershell -NoProfile -Command "Get-ChildItem 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss' | Where-Object { (Get-ItemProperty $_.PSPath).DistributionName -eq '%DOCKER_WSL_CONTAINER%' } | Select-Object -ExpandProperty PSChildName"') do (
		reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss\%%A" /v DefaultUid /t REG_DWORD /d 0 /f >nul
	)
	echo [wsl2] > "%USERPROFILE%\.wslconfig"
	echo memory=4GB >> "%USERPROFILE%\.wslconfig"
	wsl --shutdown
	echo %ESC%[33m=============== WSL2 OK ===============%ESC%[0m
)
goto :restart_script

:install_docker
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	echo Installing Docker inside WSL2…
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "echo 'WSL is ready'" >nul 2>&1
	if errorlevel 1 (
		echo %ESC%[31m=============== WSL %DOCKER_WSL_CONTAINER% is not ready. Initializing…%ESC%[0m
		wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "apt-get update" >nul 2>&1
		wsl --shutdown
		timeout /t 3 /nobreak >nul
	)
	echo Downloading and installing Docker…
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "apt-get update && apt-get install -y curl"
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "curl -fsSL https://get.docker.com | SKIP_SLEEP=1 sh"
	if errorlevel 1 (
		echo %ESC%[31m=============== docker install failed.%ESC%[0m
		echo Try running: wsl --user root -d %DOCKER_WSL_CONTAINER%
		echo Then manually run: curl -fsSL https://get.docker.com ^| sh
		goto :failed
	)
	echo Enabling systemd…
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "echo '[boot]' > /etc/wsl.conf && echo 'systemd=true' >> /etc/wsl.conf"
	wsl --shutdown
	echo %ESC%[33m=============== docker OK ===============%ESC%[0m
)
goto :restart_script

:install_conda
if not "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	echo Installing Miniforge…
	call "%PS_EXE%" %PS_ARGS% -Command "Invoke-WebRequest -Uri '%CONDA_URL%' -OutFile '%CONDA_INSTALLER%'"
	call start /wait "" "%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D="%SAFE_USERPROFILE%\Miniforge3"
	where.exe /Q conda
	if not errorlevel 1 (
		echo %ESC%[32m=============== Miniforge3 OK ===============%ESC%[0m
		findstr /i /x "Miniforge3" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo Miniforge3>>"%INSTALLED_LOG%"
		)
	) else (
		echo %ESC%[31m=============== Miniforge3 failed.%ESC%[0m
		goto :failed
	)
	if not exist "%SAFE_USERPROFILE%\.condarc" (
		call conda config --set auto_activate_base false
	)
	call conda update --all -y
	call conda clean --index-cache -y
	call conda clean --packages --tarballs -y
	del "%CONDA_INSTALLER%"
)
goto :restart_script

:download_tessdata
setlocal
set "_LANG=%~1"
set "_DEST=%~2"
"%PS_EXE%" %PS_ARGS% -Command "Invoke-WebRequest -Uri '%TESSDATA_BASE_URL%/%_LANG%.traineddata' -OutFile '%_DEST%\%_LANG%.traineddata' -ErrorAction Stop"
set "RC=%errorlevel%"
endlocal & exit /b %RC%

:install_programs
echo Installing missing programs…
setlocal EnableDelayedExpansion
for %%p in (%missing_prog_array%) do (
	set "prog=%%p"
	call "%PS_EXE%" %PS_ARGS% -Command "scoop install %%p"
	if "%%p"=="tesseract" (
		where.exe /Q !prog!
		if not errorlevel 1 (
			call :get_iso3_lang "%OS_LANG%"
			echo Detected system language: %OS_LANG% → downloading OCR language: !ISO3_LANG!
			set "tessdata=%SCOOP_APPS%\tesseract\current\tessdata"
			if not exist "!tessdata!" mkdir "!tessdata!"
			if not exist "!tessdata!\!ISO3_LANG!.traineddata" (
				call :download_tessdata "!ISO3_LANG!" "!tessdata!" || goto :failed
			)
			if exist "!tessdata!\!ISO3_LANG!.traineddata" (
				echo Tesseract OCR language !ISO3_LANG! installed in !tessdata!
			) else (
				echo Failed to install OCR language !ISO3_LANG!
			)
		)
	)
	if "%%p"=="python" (
		set "PY_FOUND="
		where.exe /Q python  && set PY_FOUND=1
		where.exe /Q python3 && set PY_FOUND=1
		where.exe /Q py      && set PY_FOUND=1
		if not defined PY_FOUND (
			echo %ESC%[31m=============== %%p failed.%ESC%[0m
			goto :failed
		)
	)
	if "%%p"=="nodejs" (
		set "prog=node"
	)
	if "%%p"=="ffmpeg-shared" (
		set "prog=ffmpeg"
		if exist "%SAFE_USERPROFILE%\scoop\apps\ffmpeg-shared\current\bin\ffmpeg.exe" (
			set "_FFMPEG_PATH=%SAFE_USERPROFILE%\scoop\apps\ffmpeg-shared\current\bin"
			echo !PATH! | findstr /i /c:"!_FFMPEG_PATH!" >nul 2>&1 || (
				set "PATH=!_FFMPEG_PATH!;!PATH!"
			)
		)
	)
	if "%%p"=="rustup" (
		if exist "%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin\rustup.exe" (
			set "_RUSTUP_PATH=%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin"
			echo !PATH! | findstr /i /c:"!_RUSTUP_PATH!" >nul 2>&1 || (
				set "PATH=!_RUSTUP_PATH!;!PATH!"
			)
		)
	)
	where.exe /Q !prog!
	if not errorlevel 1 (
		echo %ESC%[32m=============== %%p OK! ===============%ESC%[0m
		findstr /i /x "%%p" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo %%p>>"%INSTALLED_LOG%"
		)
	) else (
		echo %ESC%[31m=============== %%p failed.%ESC%[0m
		goto :failed
	)
)
endlocal & set "PATH=%PATH%"
call "%PS_EXE%" %PS_ARGS% -Command "$cp=[System.Environment]::GetEnvironmentVariable('Path','User'); $np=$cp; @('%SCOOP_SHIMS%','%SCOOP_APPS%','%CONDA_PATH%','%NODE_PATH%') | Where-Object {$_ -and $cp -notlike ('*'+$_+'*')} | ForEach-Object {$np+=(';'+$_)}; [System.Environment]::SetEnvironmentVariable('Path',$np,'User')"
set "missing_prog_array="
goto :main

:check_conda
where.exe /Q conda
if errorlevel 1 (
	echo Conda is not installed.
	exit /b 1
)
set "DETECTED_BASE="
for /f "usebackq delims=" %%B in (`conda info --base 2^>nul`) do set "DETECTED_BASE=%%B"
if not defined DETECTED_BASE (
	echo Failed to query 'conda info --base'; aborting.
	exit /b 3
)
set "CONDA_HOME=%DETECTED_BASE%"
set "CONDA_PATH=%DETECTED_BASE%\condabin"
set "CONDA_ENV=%DETECTED_BASE%\condabin\conda.bat"
set "PATH=%CONDA_PATH%;%PATH%"
set "CURRENT_ENV="
if defined CONDA_DEFAULT_ENV (
	if /i not "%CONDA_DEFAULT_ENV%"=="base" (
		set "CURRENT_ENV=%CONDA_PREFIX%"
	)
)
if defined VIRTUAL_ENV (
	set "CURRENT_ENV=%VIRTUAL_ENV%"
)
if defined CURRENT_ENV (
	echo Current python virtual environment detected: %CURRENT_ENV%.
	echo =============== This script runs with its own virtual env and must be out of any other virtual environment when it's launched.
	exit /b 2
)
if /i "%CONDA_DEFAULT_ENV%"=="base" (
	call conda deactivate >nul 2>&1
)
if not exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%\.provisioned" (
	if exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" (
		echo Detected incomplete %PYTHON_ENV% — removing and recreating...
		rmdir /s /q "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
	)
	echo Creating ./%PYTHON_ENV% with python %PYTHON_VERSION%...
	call "%CONDA_HOME%\Scripts\activate.bat"
	call conda create --prefix "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" -c conda-forge python=%PYTHON_VERSION% pip -y
	if errorlevel 1 exit /b 3
	call conda activate "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
	call :provision_env
	if errorlevel 1 exit /b 3
	> "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%\.provisioned" echo %APP_VERSION%
)
exit /b 0

:provision_env
setlocal enabledelayedexpansion
set "RC=0"
call :check_device_info %SCRIPT_MODE%
if errorlevel 1 (
	set "RC=1"
	goto :provision_env_end
)
call :install_device_packages
if errorlevel 1 (
	set "RC=1"
	goto :provision_env_end
)
call :install_python_packages
if errorlevel 1 (
	set "RC=1"
	goto :provision_env_end
)
:provision_env_end
endlocal & exit /b %RC%

:check_wsl
where.exe /Q wsl
if errorlevel 1 (
    echo WSL is not installed.
    exit /b 1
)
for /f "tokens=3" %%A in (
    'reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss" /v DefaultVersion 2^>nul ^| find "DefaultVersion"'
) do set "WSL_VERSION=%%A"
if not "%WSL_VERSION%"=="0x2" (
    echo WSL2 is not configured as default.
    exit /b 1
)
wsl -l -q 2>nul | findstr /R /C:".*" >nul
if errorlevel 1 (
    echo No WSL Linux distribution installed.
    exit /b 1
)
for /f "delims=" %%a in ('wsl echo $WSL_DISTRO_NAME') do set "DOCKER_WSL_CONTAINER=%%a"
exit /b 0

:check_docker
if "%DOCKER_MODE%"=="podman" (
	where.exe /Q podman-compose.exe
	if not errorlevel 1 (
		podman-compose version >nul 2>&1
		if not errorlevel 1 (
			echo Podman Desktop detected.
			set "PODMAN_DESKTOP=1"
			exit /b 0
		)
	)
	echo Podman is not installed.
	exit /b 1
)
where.exe /Q docker.exe
if not errorlevel 1 (
	docker version >nul 2>&1
	if not errorlevel 1 (
		echo Docker Desktop detected.
		set "DOCKER_DESKTOP=1"
		exit /b 0
	)
)
wsl --user root -d %DOCKER_WSL_CONTAINER% -- which docker >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed inside WSL2.
    exit /b 1
)
exit /b 0

:check_docker_daemon
if "%PODMAN_DESKTOP%"=="1" exit /b 0
if "%DOCKER_DESKTOP%"=="1" (
    docker info >nul 2>&1
    if not errorlevel 1 exit /b 0
    echo Docker Desktop daemon is not running. Please start Docker Desktop.
    exit /b 1
)
wsl --user root -d %DOCKER_WSL_CONTAINER% -- docker info >nul 2>&1
if not errorlevel 1 exit /b 0
echo Starting Docker daemon inside WSL2…
wsl --user root -d %DOCKER_WSL_CONTAINER% -- service docker start >nul 2>&1
if errorlevel 1 (
    echo Docker failed to start
    exit /b 1
)
set "DOCKER_RETRIES=0"
:wait_docker
timeout /t 3 /nobreak >nul
set /a DOCKER_RETRIES+=1
if %DOCKER_RETRIES% geq 20 (
    echo Docker daemon failed to start after 60 seconds.
    exit /b 1
)
wsl --user root -d %DOCKER_WSL_CONTAINER% -- docker info >nul 2>&1
if errorlevel 1 goto :wait_docker
echo Docker daemon is ready.
exit /b 0

:check_device_info
set "ARG=%~1"
for /f "delims=" %%I in ('python -c "import sys; from lib.classes.device_installer import DeviceInstaller as D; r=D().check_device_info(sys.argv[1]); print(r if r else '')" "%ARG%"') do set "DEVICE_INFO_STR=%%I"
if "%DEVICE_INFO_STR%"=="" (
	echo DEVICE_INFO_STR is empty
	exit /b 1
)
exit /b 0

:json_get
setlocal enabledelayedexpansion
set "KEY=%~1"
set "JSON_VALUE="
for /f "delims=" %%i in ('powershell -Command "$env:DEVICE_INFO_STR | ConvertFrom-Json | Select-Object -ExpandProperty %KEY%"') do set "JSON_VALUE=%%i"
if "!JSON_VALUE!"=="" (
    echo No key nor value found for %KEY%
    endlocal & exit /b 1
)
endlocal & set "DEVICE_TAG=%JSON_VALUE%"
exit /b 0

:install_device_packages
"%PS_EXE%" %PS_ARGS% -Command ^
"python -c \"import sys, os; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_device_packages(os.environ.get('DEVICE_INFO_STR', '')))\""
exit /b %errorlevel%

:install_python_packages
echo Installing python dependencies…
"%PS_EXE%" %PS_ARGS% -Command ^
"python -c \"import sys; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_python_packages())\""
exit /b %errorlevel%

:check_sitecustomized
set "src_pyfile=%SAFE_SCRIPT_DIR%\components\sitecustomize.py"
for /f "delims=" %%a in ('python -c "import sysconfig;print(sysconfig.get_paths()[\"purelib\"])"') do (
    set "site_packages_path=%%a"
)
if "%site_packages_path%"=="" (
    echo [WARN] Could not detect Python site-packages
    exit /b 1
)
set "dst_pyfile=%site_packages_path%\sitecustomize.py"
if not exist "%dst_pyfile%" (
    copy /y "%src_pyfile%" "%dst_pyfile%" >nul
    if errorlevel 1 (
        echo %ESC%[31m=============== sitecustomize.py hook error: copy failed.%ESC%[0m
        exit /b 1
    )
    exit /b 0
)
:: xcopy /d only overwrites when source is newer than destination
:: destination ends with '\' so xcopy treats it as a directory, no F/D prompt, no wildcard target
xcopy /d /y "%src_pyfile%" "%site_packages_path%\" >nul
if errorlevel 1 (
    echo %ESC%[31m=============== sitecustomize.py hook update failed.%ESC%[0m
    exit /b 1
)
exit /b 0

:build_docker_image
setlocal enabledelayedexpansion
set "ARG=%~1"
if defined ARG (
    set "ARG_ESCAPED=%ARG:"=\"%"
) else (
    set "ARG_ESCAPED="
)
if "%DOCKER_MODE%"=="podman" (
	if "%PODMAN_DESKTOP%"=="0" (
		echo podman-compose is not running.
		endlocal 
		exit /b 1
	)
) else if "%DOCKER_MODE%"=="compose" (
	if "%DOCKER_DESKTOP%"=="0" (
		echo docker compose is not running.
		endlocal 
		exit /b 1
	)
)
set "DOCKER_IMG_NAME=%DOCKER_IMG_NAME%:%DEVICE_TAG%"
set "cmd_options="
set "py_vers=%PYTHON_VERSION%"
if /i "%DEVICE_TAG:~0,2%"=="cu" (
    set "cmd_options=--gpus all"
) else if /i "%DEVICE_TAG:~0,6%"=="jetson" (
    set "cmd_options=--runtime nvidia --gpus all"
    set "py_vers=%MIN_PYTHON_VERSION%"
) else if /i "%DEVICE_TAG:~0,8%"=="rocm" (
    set "cmd_options=--device=/dev/kfd --device=/dev/dri"
) else if /i "%DEVICE_TAG%"=="xpu" (
    set "cmd_options=--device=/dev/dri"
) else if /i "%DEVICE_TAG%"=="mps" (
    set "cmd_options="
) else if /i "%DEVICE_TAG%"=="cpu" (
    set "cmd_options="
)
if /i "%DEVICE_TAG%"=="cpu" (
    set "COMPOSE_PROFILES=cpu"
) else if /i "%DEVICE_TAG%"=="mps" (
    set "COMPOSE_PROFILES=cpu"
) else (
    set "COMPOSE_PROFILES=gpu"
)
if "%DOCKER_DESKTOP%"=="1" (
	set "wsl_cmd="
    set "WSL_DIR=%SAFE_SCRIPT_DIR%"
) else (
	set "wsl_cmd=wsl --user root -d %DOCKER_WSL_CONTAINER% --"
    for /f "delims=" %%i in ('wsl --user root -d %DOCKER_WSL_CONTAINER% -- wslpath "%SAFE_SCRIPT_DIR:\=/%"') do set "WSL_DIR=%%i"
)
call :get_iso3_lang "%OS_LANG%"
set "ISO3_LANG=!ISO3_LANG!"
if "%DOCKER_MODE%"=="podman" (
    echo Using podman-compose
    set "PODMAN_BUILD_ARGS=--format docker --no-cache --network=host"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg PYTHON_VERSION=%py_vers%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg APP_VERSION=%APP_VERSION%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DEVICE_TAG=%DEVICE_TAG%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DOCKER_DEVICE_STR=%ARG_ESCAPED%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DOCKER_PROGRAMS_STR=%DOCKER_PROGRAMS%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg CALIBRE_INSTALLER_URL=%DOCKER_CALIBRE_INSTALLER_URL%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg ISO3_LANG=%ISO3_LANG%"
    cd /d "%SAFE_SCRIPT_DIR%"
    podman-compose -f podman-compose.yml --profile %COMPOSE_PROFILES% build
	if errorlevel 1 (
		echo Build failed
		endlocal 
		exit /b 1
	)
	echo Docker image ready. To run your docker:
	echo Podman Compose:
	echo 	GUI mode:
	echo 		podman-compose -f podman-compose.yml --profile %COMPOSE_PROFILES% up
	echo 	Headless mode:
	echo   		podman-compose -f podman-compose.yml --profile %COMPOSE_PROFILES% run --rm -v "/mnt/c/Users/myname/whatever/custom_voice:/app/custom_voice" ebook2audiobook --headless --ebook "/app/ebooks/tests/test_eng.txt" --tts_engine yourtts --language eng --voice "/app/Desktop/myvoice.wav" etc.
) else if "%DOCKER_MODE%"=="compose" (
    if "%DOCKER_DESKTOP%"=="1" (
		echo Using docker compose
        docker compose --progress=plain --profile "%COMPOSE_PROFILES%" build --no-cache --build-arg PYTHON_VERSION="%py_vers%" --build-arg APP_VERSION="%APP_VERSION%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%" --build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" --build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" --build-arg ISO3_LANG="%ISO3_LANG%"
    ) else (
		echo Using docker compose into WSL2 %DOCKER_WSL_CONTAINER%
        %wsl_cmd% bash -c "cd '%WSL_DIR%' && docker compose --progress=plain --profile '%COMPOSE_PROFILES%' build --no-cache --build-arg PYTHON_VERSION='%py_vers%' --build-arg APP_VERSION='%APP_VERSION%' --build-arg DEVICE_TAG='%DEVICE_TAG%' --build-arg DOCKER_DEVICE_STR=\"%ARG_ESCAPED%\" --build-arg DOCKER_PROGRAMS_STR='%DOCKER_PROGRAMS%' --build-arg CALIBRE_INSTALLER_URL='%DOCKER_CALIBRE_INSTALLER_URL%' --build-arg ISO3_LANG='%ISO3_LANG%'"
    )
	if errorlevel 1 (
		echo Build failed
		endlocal 
		exit /b 1
	)
	if defined wsl_cmd (
		set "env_prefix=DEVICE_TAG=%DEVICE_TAG%"
	) else (
		set "env_prefix=set "DEVICE_TAG=%DEVICE_TAG%" ^&^&"
	)
	echo Docker image ready. To run your docker:
	echo Docker Compose:
	echo 	GUI mode:
	echo 		%env_prefix% docker compose --profile %COMPOSE_PROFILES% up --no-log-prefix
	echo 	Headless mode:
	echo   		%env_prefix% docker compose --profile %COMPOSE_PROFILES% run --rm -v "/mnt/c/Users/myname/whatever/custom_voice:/app/custom_voice" ebook2audiobook --headless --ebook "/app/ebooks/tests/test_eng.txt" --tts_engine yourtts --language eng --voice "/app/Desktop/myvoice.wav" etc.
) else (
	if "%DOCKER_DESKTOP%"=="1" (
		:: echo Using docker buildx
		:: docker buildx use default
        :: docker buildx build --shm-size=4g --progress=plain --no-cache --platform linux/amd64 --build-arg PYTHON_VERSION="%py_vers%" --build-arg APP_VERSION="%APP_VERSION%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%" --build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" --build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" --build-arg ISO3_LANG="%ISO3_LANG%" -t "%DOCKER_IMG_NAME%" .
		echo Using docker build
		docker build --shm-size=4g --progress=plain --no-cache --build-arg PYTHON_VERSION="%py_vers%" --build-arg APP_VERSION="%APP_VERSION%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%" --build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" --build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" --build-arg ISO3_LANG="%ISO3_LANG%" -t "%DOCKER_IMG_NAME%" .
		docker image prune --force
	) else (
		echo Using docker build into WSL2 %DOCKER_WSL_CONTAINER%
		%wsl_cmd% bash -c "service docker status >/dev/null 2>&1 || service docker start"
		timeout /t 3 /nobreak >nul
		:: buildx builder setup no longer needed with docker build
		:: %wsl_cmd% bash -c "cd '%WSL_DIR%' && docker buildx use wslbuilder 2>/dev/null || docker buildx create --name wslbuilder --use"
		:: if errorlevel 1 (
		:: 	echo Failed to setup buildx builder
		:: 	endlocal 
		:: 	exit /b 1
		:: )
		%wsl_cmd% bash -c "cd '%WSL_DIR%' && docker build --shm-size=4g --progress=plain --no-cache --build-arg PYTHON_VERSION='%py_vers%' --build-arg APP_VERSION='%APP_VERSION%' --build-arg DEVICE_TAG='%DEVICE_TAG%' --build-arg DOCKER_DEVICE_STR='%ARG_ESCAPED%' --build-arg DOCKER_PROGRAMS_STR='%DOCKER_PROGRAMS%' --build-arg CALIBRE_INSTALLER_URL='%DOCKER_CALIBRE_INSTALLER_URL%' --build-arg ISO3_LANG='%ISO3_LANG%' -t '%DOCKER_IMG_NAME%' ."
		if errorlevel 1 (
			echo Build failed
			endlocal 
			exit /b 1
		)
		%wsl_cmd% docker image prune --force
		echo Docker image ready. To run your docker:
		echo GUI mode:
		echo     %wsl_cmd% docker run -v ".\ebooks:/app/ebooks" -v ".\audiobooks:/app/audiobooks" -v ".\models:/app/models" -v ".\voices:/app/voices" -v ".\tmp:/app/tmp" !cmd_options!--rm -it -p 7860:7860 %DOCKER_IMG_NAME%
		echo Headless mode:
		echo     %wsl_cmd% docker run -v ".\ebooks:/app/ebooks" -v ".\audiobooks:/app/audiobooks" -v ".\models:/app/models" -v ".\voices:/app/voices" -v ".\tmp:/app/tmp" -v "D:\path\to\custom\voices:/app/custom_voice" !cmd_options!--rm -it -p 7860:7860 %DOCKER_IMG_NAME% --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/custom_voice/voice.wav etc..]
	)
)
if "%DOCKER_DESKTOP%"=="1" (
	set "wsl_cmd=wsl --user root -d %DOCKER_WSL_CONTAINER% --"
)
endlocal
exit /b 0

:::::::::::: END CORE FUNCTIONS

:main
if defined arguments.help (
    if /i "%arguments.help%"=="true" (
		call :check_python
		if errorlevel 1 goto :install_python
		call :check_docker
		if "%DOCKER_DESKTOP%"=="0" (
			ifi "%PODMAN_DESKTOP"=="0" (
				wsl --user root -d %DOCKER_WSL_CONTAINER% -- which docker >nul 2>&1
				if not errorlevel 1 (
					set DOCKER_IN_WSL=1
				)
			)
		)
        call python -u "%SAFE_SCRIPT_DIR%\app.py" %ARGS%
        goto :eof
    )
) else (
    if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
        if "%DOCKER_DEVICE_STR%"=="" (
			setlocal enabledelayedexpansion
			call :check_python
			if errorlevel 1 goto :install_python
			call :check_wsl
			if errorlevel 1 goto :install_wsl
            call :check_docker
            if errorlevel 1	(
				if not "%DOCKER_MODE%"=="podman" (
					goto :install_docker
				) else (
					goto :failed
				)
            )
			call :check_docker_daemon
            if errorlevel 1 goto :failed
            call :check_device_info %SCRIPT_MODE%
            if errorlevel 1 goto :failed
			call :install_device_packages
            if "!DEVICE_TAG!"=="" (
                call :json_get tag
                if errorlevel 1 goto :failed
            )
			if "%PODMAN_DESKTOP%"=="1" (
				podman image exists "%DOCKER_IMG_NAME%:!DEVICE_TAG!" >nul 2>&1
			) else if "%DOCKER_DESKTOP%"=="1" (
				docker image inspect "%DOCKER_IMG_NAME%:!DEVICE_TAG!" >nul 2>&1
			) else (
				wsl --user root -d %DOCKER_WSL_CONTAINER% -- docker image inspect "%DOCKER_IMG_NAME%:!DEVICE_TAG!" >nul 2>&1
			)
			if not errorlevel 1 (
				echo [STOP] Docker image "%DOCKER_IMG_NAME%:!DEVICE_TAG!" already exists.
				if "%DOCKER_DESKTOP%"=="1" (
					echo To rebuild, first remove it with: docker rmi %DOCKER_IMG_NAME%:!DEVICE_TAG! --force
				) else (
					echo To rebuild, first remove it with: wsl -d %DOCKER_WSL_CONTAINER% -- docker rmi %DOCKER_IMG_NAME%:!DEVICE_TAG! --force
				)
				goto :failed
			)
            call :build_docker_image "!DEVICE_INFO_STR!"
            if errorlevel 1 goto :failed
			endlocal
        ) else (
			echo The Docker image is only available with a Linux container
        )
    ) else if "%SCRIPT_MODE%"=="%NATIVE%" (
		call :check_scoop
		if errorlevel 1 goto :install_scoop
		call :check_scoop_buckets
		if errorlevel 1 goto :install_scoop_buckets
		call :check_programs
		if errorlevel 1 goto :install_programs
		call :check_conda
		if errorlevel 3 goto :failed
		if errorlevel 2 goto :eof
		if errorlevel 1 goto :install_conda
        call conda activate "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
		if errorlevel 1 goto :failed
        call :check_sitecustomized
        if errorlevel 1 goto :failed
        call :build_gui
        call python.exe -u "%SAFE_SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
		call conda deactivate >nul && call conda deactivate >nul
    ) else if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
        call :check_sitecustomized
        if errorlevel 1 goto :failed
        call python.exe -u "%SAFE_SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
	)
)
goto :eof

:failed
echo =============== ebook2audiobook is not correctly installed.
where.exe /Q conda && (
    call conda deactivate >nul && call conda deactivate >nul
)
exit /b 1

:quit
set "CODE=%~1"
endlocal
exit /b %CODE%

:restart_script
net session >nul 2>&1
if not errorlevel 1 (
    echo Restarting as normal user %USERNAME%…
    schtasks /create /tn "RestartScript" /tr "cmd /k cd /d \"%SAFE_SCRIPT_DIR%\" & call %APP_FILE% %ARGS%" /sc once /st 00:00 /ru "%USERNAME%" /it /f >nul 2>&1
    schtasks /run /tn "RestartScript" >nul 2>&1
    timeout /t 2 /nobreak >nul
    schtasks /delete /tn "RestartScript" /f >nul 2>&1
    exit 0
)
start "%APP_NAME%" cmd /k "cd /d "%SAFE_SCRIPT_DIR%" & call %APP_FILE% %ARGS%"
exit 0

:restart_script_admin
echo Restarting script as Administrator…
call "%PS_EXE%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%SAFE_SCRIPT_DIR%\%APP_FILE%' -ArgumentList '%ARGS%' -Verb RunAs"
exit

endlocal
pause