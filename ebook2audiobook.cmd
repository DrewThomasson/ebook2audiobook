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
set "SCRIPT_MODE=%NATIVE%"
set "APP_NAME=ebook2audiobook"
set /p APP_VERSION=<"%SAFE_SCRIPT_DIR%\VERSION.txt"
set "APP_FILE=%APP_NAME%.cmd"
set "OS_LANG=%LANG%" & if "%OS_LANG%"=="" set "OS_LANG=en" & call set "OS_LANG=%%OS_LANG:~0,2%%"
set "TEST_HOST=127.0.0.1"
set "TEST_PORT=7860"
set "ICON_PATH=%SAFE_SCRIPT_DIR%\tools\icons\windows\appIcon.ico"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "STARTMENU_LNK=%STARTMENU_DIR%\%APP_NAME%.lnk"
set "DESKTOP_LNK=%SAFE_USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "ARCH=%PROCESSOR_ARCHITECTURE%" & if defined PROCESSOR_ARCHITEW6432 set "ARCH=%PROCESSOR_ARCHITEW6432%"
set "PYTHON_VERSION=3.12"
set "PYTHON_SCOOP=python%PYTHON_VERSION:.=%"
set "PYTHON_ENV=python_env"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="
set "HOST_PROGRAMS=cmake rustup python calibre ffmpeg mediainfo nodejs espeak-ng sox tesseract"
set "DOCKER_PROGRAMS=ffmpeg mediainfo nodejs espeak-ng sox tesseract-ocr" # tesseract-ocr-[lang] and calibre are hardcoded in Dockerfile
set "DOCKER_CALIBRE_INSTALLER_URL=https://download.calibre-ebook.com/linux-installer.sh"
set "DOCKER_DEVICE_STR="
set "DOCKER_IMG_NAME=athomasson2/%APP_NAME%"
set "DEVICE_INFO_STR="
set "TMP=%SAFE_SCRIPT_DIR%\tmp"
set "TEMP=%SAFE_SCRIPT_DIR%\tmp"
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
set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%;%PATH%"
set "INSTALLED_LOG=%SAFE_SCRIPT_DIR%\.installed"
set "UNINSTALLER=%SAFE_SCRIPT_DIR%\uninstall.cmd"
set "BROWSER_HELPER=%SAFE_SCRIPT_DIR%\.bh.ps1"
set "HELP_FOUND=%ARGS:--help=%"
set "HEADLESS_FOUND=%ARGS:--headless=%"
set "WSL_VERSION="

IF NOT DEFINED DEVICE_TAG SET "DEVICE_TAG="

set "OK_SCOOP=0"
set "OK_CONDA=0"
set "OK_PROGRAMS=0"
set "OK_WSL=0"
set "OK_DOCKER=0"
set "OK_DOCKER_BUILDX=0"

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "PATH=%%B;%PATH%"
)

if "%ARCH%"=="X86" (
    echo %ESC%[31m=============== Error: 32-bit architecture is not supported.%ESC%[0m
    goto :failed
)

if not exist "%INSTALLED_LOG%" if /I not "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
    type nul > "%INSTALLED_LOG%"
)

cd /d "%SAFE_SCRIPT_DIR%"

:: Clear previous associative values
for /f "tokens=1* delims==" %%A in ('set arguments. 2^>nul') do set "%%A="

::::::::::::::::::::::::::::::: CORE FUNCTIONS

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
    if /I "%arguments.script_mode%"=="%BUILD_DOCKER%" (
        set "SCRIPT_MODE=%arguments.script_mode%"
    ) else (
        echo Error: Invalid script mode argument: %arguments.script_mode%
        goto :failed
    )
)
if defined arguments.docker_device (
    set "DOCKER_DEVICE_STR=%arguments.docker_device%"
    if /i "%arguments.docker_device%"=="true" (
        echo Error: --docker_device has no value
        goto :failed
    )
)
if defined arguments.script_mode (
    if /I "%arguments.script_mode%"=="true" (
        echo Error: --script_mode requires a value
        goto :failed
    )
	for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do (
		set "argname=%%A"
		call set "argname=%%argname:arguments.=%%"

		if not "%argname%"=="" (
			if /I not "%argname%"=="script_mode" (
				if /I not "%argname%"=="docker_device" (
					echo Error: when --script_mode is used, only --docker_device is allowed as additional option. Invalid option: --%argname%
					goto :failed
				)
			)
		)
	)
)
goto :check_scoop

::::::::::::::: DESKTOP APP
:make_shortcut
set "shortcut=%~1"
"%PS_EXE%" %PS_ARGS% -Command "$s=New-Object -ComObject WScript.Shell; $sc=$s.CreateShortcut('%shortcut%'); $sc.TargetPath='cmd.exe'; $sc.Arguments='/k ""cd /d """"%SAFE_SCRIPT_DIR%"""" && """"%APP_FILE%""""""'; $sc.WorkingDirectory='%SAFE_SCRIPT_DIR%'; $sc.IconLocation='%ICON_PATH%'; $sc.Save()"
exit /b

:build_gui
if /I not "%HEADLESS_FOUND%"=="%ARGS%" (
    if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
    if not exist "%STARTMENU_LNK%" (
        call :make_shortcut "%STARTMENU_LNK%"
        call :make_shortcut "%DESKTOP_LNK%"
    )
    for /f "skip=1 delims=" %%L in ('tasklist /v /fo csv /fi "imagename eq powershell.exe" 2^>nul') do (
        echo %%L | findstr /I "%APP_NAME%" >nul && (
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
exit /b
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

:check_scoop
where.exe /Q scoop
if errorlevel 1 (
    echo Scoop is not installed.
    set "OK_SCOOP=1"
    goto :install_programs
) else (
    if exist "%SAFE_SCRIPT_DIR%\.after-scoop" (
        call "%PS_EXE%" %PS_ARGS% -Command "scoop install git; scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git; scoop bucket add extras; scoop bucket add versions" || goto :failed
        call git config --global credential.helper
        echo %ESC%[32m=============== Scoop components OK ===============%ESC%[0m
        set "OK_SCOOP=0"
        findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
        if errorlevel 1 (
            echo scoop>>"%INSTALLED_LOG%"
        )
        del "%SAFE_SCRIPT_DIR%\.after-scoop" >nul 2>&1
    )
)
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
    goto :check_required_programs
) else (
    goto :check_conda
)
exit /b

:check_required_programs
set "missing_prog_array="
setlocal EnableDelayedExpansion
for %%p in (%HOST_PROGRAMS%) do (
    set "prog=%%p"
    if "%%p"=="nodejs" set "prog=node"
    where.exe /Q !prog!
    if errorlevel 1 (
        set "missing_prog_array=!missing_prog_array! %%p"
    )
)
endlocal & set "missing_prog_array=%missing_prog_array%"
if not "%missing_prog_array%"=="" (
    set "OK_PROGRAMS=1"
    goto :install_programs
)
goto :dispatch

:install_programs
if not "%OK_SCOOP%"=="0" (
    echo Installing Scoop…
    call "%PS_EXE%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command ^
        "Set-ExecutionPolicy Bypass Process -Force; iwr -useb https://get.scoop.sh | iex"
    echo %ESC%[33m=============== Scoop OK ===============%ESC%[0m
    type nul > "%SAFE_SCRIPT_DIR%\.after-scoop"
	goto :restart_script
)
if not "%OK_WSL%"=="0" (
	if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
		echo WSL2 is required to build Linux containers.
		net session >nul 2>&1
		if errorlevel 1 (
			echo The script will install WSL2 in Administrator mode.
			pause
			echo Restarting script as Administrator…
			goto :restart_script_admin
		)
		echo Installing WSL2…
		wsl --install
		dism /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
		dism /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
		wsl --set-default-version 2
		wsl --install -d Ubuntu
		echo.
		echo ==================================================
		echo WSL installation triggered.
		echo please reboot manually now.
		echo ==================================================
		pause
		exit
	)
)
if not "%OK_DOCKER%"=="0" (
	if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
		echo Installing Docker…
		call "%PS_EXE%" %PS_ARGS% -Command "scoop install docker docker-buildx"
		if exist "%SCOOP_SHIMS%\docker.exe" (
			echo Registering docker service…
			dockerd --register-service >nul 2>&1
			echo %ESC%[33m=============== docker OK ===============%ESC%[0m
			goto :restart_script
		) else (
			echo %ESC%[31m=============== docker install failed.%ESC%[0m
			goto :failed
		)
	)
)
if not "%OK_DOCKER_BUILDX%"=="0" (
	if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
		echo Installing docker-buildx…
		call "%PS_EXE%" %PS_ARGS% -Command "scoop install docker-buildx"
		if exist "%SCOOP_SHIMS%\docker-buildx.exe" (
			echo %ESC%[33m=============== docker-buildx OK ===============%ESC%[0m
			set "OK_DOCKER_BUILDX=0"
			goto :dispatch
		) else (
			echo %ESC%[31m=============== docker-buildx install failed.%ESC%[0m
			goto :failed
		)
	)
)
if not "%OK_CONDA%"=="0" (
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
			call conda config --set auto_activate false
		)
		call conda update --all -y
		call conda clean --index-cache -y
		call conda clean --packages --tarballs -y
		del "%CONDA_INSTALLER%"
		set "OK_CONDA=0"
		goto :restart_script
	)
)
if not "%OK_PROGRAMS%"=="0" (
    echo Installing missing programs…
    if "%OK_SCOOP%"=="0" (
        call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git"
        call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add extras"
        call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add versions"
    )
	setlocal EnableDelayedExpansion
    for %%p in (%missing_prog_array%) do (
        set "prog=%%p"
        call "%PS_EXE%" %PS_ARGS% -Command "scoop install %%p"
        if "%%p"=="tesseract" (
            where.exe /Q !prog!
            if not errorlevel 1 (
                call :get_iso3_lang "!OS_LANG!"
                echo Detected system language: !OS_LANG! → downloading OCR language: !ISO3_LANG!
                set "tessdata=%SCOOP_APPS%\tesseract\current\tessdata"
                if not exist "!tessdata!" mkdir "!tessdata!"
                if not exist "!tessdata!\!ISO3_LANG!.traineddata" (
                    call "%PS_EXE%" %PS_ARGS% -Command "Invoke-WebRequest -Uri 'https://github.com/tesseract-ocr/tessdata_best/raw/main/!ISO3_LANG!.traineddata' -OutFile '!tessdata!\!ISO3_LANG!.traineddata' -ErrorAction Stop" || goto :failed
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
		if "%%p"=="rustup" (
			if exist "%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin\rustup.exe" (
				set "PATH=%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin;!PATH!"
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
	endlocal
    call "%PS_EXE%" %PS_ARGS% -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%', 'User')"
    set "OK_SCOOP=0"
    set "OK_PROGRAMS=0"
    set "missing_prog_array="
)
goto :dispatch

:check_conda
where.exe /Q conda
if errorlevel 1 (
    echo Miniforge3 is not installed.
    set "OK_CONDA=1"
    goto :install_programs
)
:: Check if running in a Conda environment
if defined CONDA_DEFAULT_ENV (
    set "CURRENT_ENV=%CONDA_PREFIX%"
)
:: Check if running in a Python virtual environment
if defined VIRTUAL_ENV (
    set "CURRENT_ENV=%VIRTUAL_ENV%"
)
for /f "delims=" %%i in ('where.exe python') do (
    if defined CONDA_PREFIX (
        if /i "%%i"=="%CONDA_PREFIX%\Scripts\python.exe" (
            set "CURRENT_ENV=%CONDA_PREFIX%"
            break
        )
    ) else if defined VIRTUAL_ENV (
        if /i "%%i"=="%VIRTUAL_ENV%\Scripts\python.exe" (
            set "CURRENT_ENV=%VIRTUAL_ENV%"
            break
        )
    )
)
if "%CURRENT_ENV%"=="" (
    if not exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" (
        echo Creating ./python_env version %PYTHON_VERSION%…
        call "%CONDA_HOME%\Scripts\activate.bat"
        call conda update -n base -c conda-forge conda -y
        call conda update --all -y
        call conda clean --index-cache -y
        call conda clean --packages --tarballs -y
        call conda create --prefix "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
        call conda activate base
        call conda activate "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
        call :install_python_packages
        if errorlevel 1 goto :failed
        call conda deactivate
        call conda deactivate
    )
) else (
    echo Current python virtual environment detected: %CURRENT_ENV%. 
    echo =============== This script runs with its own virtual env and must be out of any other virtual environment when it's launched.
    goto :failed
)
goto :check_required_programs

:check_docker
where.exe /Q wsl
if errorlevel 1 (
	echo WSL is not installed.
	set "OK_WSL=1"
	exit /b 1
)
for /f "tokens=3" %%A in (
	'reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Lxss" /v DefaultVersion 2^>nul ^| find "DefaultVersion"'
) do (
	set "WSL_VERSION=%%A"
)
if not "%WSL_VERSION%"=="0x2" (
	echo WSL2 is not configured as default.
	set "OK_WSL=1"
	exit /b 1
)
wsl -l -q 2>nul | findstr /R /C:".*" >nul
if errorlevel 1 (
	echo No WSL Linux distribution installed.
	set "OK_WSL=1"
	exit /b 1
)
where.exe /Q docker
if errorlevel 1 (
	echo docker is not installed.
	set "OK_DOCKER=1"
	exit /b 1
)
where.exe /Q docker-buildx
if errorlevel 1 (
	echo docker-buildx is not installed.
	set "OK_DOCKER_BUILDX=1"
	exit /b 1
)
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
echo %KEY%: !JSON_VALUE!
endlocal & set "JSON_VALUE=%JSON_VALUE%"
exit /b 0

:install_python_packages
echo Installing python dependencies…
"%PS_EXE%" %PS_ARGS% -Command ^
"python -c \"import sys; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_python_packages())\""
exit /b %errorlevel%

:install_device_packages
set "arg=%~1"
"%PS_EXE%" %PS_ARGS% -Command ^
"python -c \"import sys; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_device_packages(r'%arg%'))\""
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
for %%I in ("%src_pyfile%") do set "src_time=%%~tI"
for %%I in ("%dst_pyfile%") do set "dst_time=%%~tI"
if "%src_time%" GTR "%dst_time%" (
    copy /y "%src_pyfile%" "%dst_pyfile%" >nul
    if errorlevel 1 (
        echo %ESC%[31m=============== sitecustomize.py hook update failed.%ESC%[0m
        exit /b 1
    )
)
exit /b 0

:build_docker_image
set "ARG=%~1"
where.exe docker >nul 2>&1
if errorlevel 1 (
	echo =============== Error: Docker must be installed and running
	exit /b 1
)
where.exe podman-compose >nul 2>&1
set "HAS_PODMAN_COMPOSE=%errorlevel%"
docker compose version >nul 2>&1
set "HAS_COMPOSE=%errorlevel%"
set "DOCKER_IMG_NAME=%DOCKER_IMG_NAME%:%DEVICE_TAG%"
set "cmd_options="
set "cmd_extra="
set "py_vers=%PYTHON_VERSION% "
if /i "%DEVICE_TAG:~0,2%"=="cu" (
    set "cmd_options=--gpus all"
) else if /i "%DEVICE_TAG:~0,6%"=="jetson" (
    set "cmd_options=--runtime nvidia --gpus all"
    set "py_vers=3.10 "
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
if "%HAS_PODMAN_COMPOSE%"=="0" (
	echo --> Using podman-compose
    set "PODMAN_BUILD_ARGS=--format docker --no-cache --network=host"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg PYTHON_VERSION=%py_vers%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg APP_VERSION=%APP_VERSION%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DEVICE_TAG=%DEVICE_TAG%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DOCKER_DEVICE_STR=%ARG%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg DOCKER_PROGRAMS_STR=%DOCKER_PROGRAMS%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg CALIBRE_INSTALLER_URL=%DOCKER_CALIBRE_INSTALLER_URL%"
    set "PODMAN_BUILD_ARGS=%PODMAN_BUILD_ARGS% --build-arg ISO3_LANG=%ISO3_LANG%"
    podman-compose -f podman-compose.yml build
    if errorlevel 1 exit /b 1
) else if "%HAS_COMPOSE%"=="0" (
	echo --> Using docker-compose
    set "BUILD_NAME=%DOCKER_IMG_NAME%"
    docker compose build --progress=plain --no-cache ^
        --build-arg PYTHON_VERSION="%py_vers%" ^
        --build-arg APP_VERSION="%APP_VERSION%" ^
        --build-arg DEVICE_TAG="%DEVICE_TAG%" ^
        --build-arg DOCKER_DEVICE_STR="%ARG%" ^
        --build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" ^
        --build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" ^
        --build-arg ISO3_LANG="%ISO3_LANG%"
    if errorlevel 1 exit /b 1
) else (
	echo --> Using docker build
    docker buildx --progress=plain --no-cache ^
        --build-arg PYTHON_VERSION="%py_vers%" ^
        --build-arg APP_VERSION="%APP_VERSION%" ^
        --build-arg DEVICE_TAG="%DEVICE_TAG%" ^
        --build-arg DOCKER_DEVICE_STR="%ARG%" ^
        --build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" ^
        --build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" ^
        --build-arg ISO3_LANG="%ISO3_LANG%" ^
        -t "%DOCKER_IMG_NAME%" .
    if errorlevel 1 exit /b 1
)
if defined cmd_options set "cmd_extra=%cmd_options% "
echo Docker image ready. to run your docker:"
echo GUI mode:
echo     docker run %cmd_extra%--rm -it -p 7860:7860 %DOCKER_IMG_NAME%
echo Headless mode:
echo     docker run %cmd_extra%--rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 %DOCKER_IMG_NAME% --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
echo Docker Compose:
echo     DEVICE_TAG=%DEVICE_TAG% docker compose up -d
echo Podman Compose:
echo     DEVICE_TAG=%DEVICE_TAG% podman-compose up -d
exit /b 0

:::::::::::: END CORE FUNCTIONS

:dispatch
if "%OK_SCOOP%"=="0" (
    if "%OK_PROGRAMS%"=="0" (
        if "%OK_CONDA%"=="0" (
            if "%OK_DOCKER%"=="0" (
				if "%OK_DOCKER_BUILDX%"=="0" (
					goto :main
				)
            )
        )
    )
)
echo OK_PROGRAMS: %OK_PROGRAMS%
echo OK_CONDA: %OK_CONDA%
echo OK_DOCKER: %OK_DOCKER%
echo OK_DOCKER_BUILDX: %OK_DOCKER_BUILDX%
goto :install_programs

:main
if defined arguments.help (
    if /I "%arguments.help%"=="true" (
        where.exe /Q conda
        if errorlevel 0 (
            call conda activate "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
            call python "%SAFE_SCRIPT_DIR%\app.py" %ARGS%
            call conda deactivate
        ) else (
            echo Ebook2Audiobook must be installed before to run --help.
        )
        goto :eof
    )
) else (
    if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
        if "%DOCKER_DEVICE_STR%"=="" (
            call %PYTHON_SCOOP% --version >nul 2>&1 || call scoop install %PYTHON_SCOOP% 2>nul
            where.exe /Q %PYTHON_SCOOP%
            if errorlevel 1 (
                echo %ESC%[31m=============== %PYTHON_SCOOP% failed.%ESC%[0m
                goto :failed
            )
            call :check_docker
            if errorlevel 1	goto :install_programs
			call :check_device_info %SCRIPT_MODE%
			if "%DEVICE_INFO_STR%"=="" goto :failed
			if "%DEVICE_TAG%"=="" (
				call :json_get tag
				if "%JSON_VALUE%"=="" goto :failed
				set "DEVICE_TAG=%JSON_VALUE%"
			)
			docker image inspect "%DOCKER_IMG_NAME%:%DEVICE_TAG%" >nul 2>&1
			if not errorlevel 1 (
				echo [STOP] Docker image "%DOCKER_IMG_NAME%:%DEVICE_TAG%" already exists. Aborting build.
				echo Delete it using: docker rmi %DOCKER_IMG_NAME%:%DEVICE_TAG% --force
				goto :failed
			)
            call :build_docker_image "%DEVICE_INFO_STR%"
            if errorlevel 1 goto :failed
        ) else (
            call :install_python_packages
            if errorlevel 1 goto :failed
            call :install_device_packages "%DOCKER_DEVICE_STR%"
            if errorlevel 1 goto :failed
            call :check_sitecustomized
            if errorlevel 1 goto :failed
        )
    ) else (
        call "%CONDA_HOME%\Scripts\activate.bat"
        call conda activate base
        call conda activate "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
        call :check_sitecustomized
        if errorlevel 1 goto :failed
        call :build_gui
        call python "%SAFE_SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
        call conda deactivate >nul && call conda deactivate >nul
    )
)
exit /b 0

:failed
echo =============== ebook2audiobook is not correctly installed.
where.exe /Q conda && (
    call conda deactivate >nul 2>&1
    call conda deactivate >nul
)
exit /b 1

:quit
set "CODE=%~1"
endlocal
exit /b %CODE%

:restart_script
start "%APP_NAME%" cmd /k "cd /d ""%SAFE_SCRIPT_DIR%"" & call %APP_FILE% %ARGS%"
exit 0

:restart_script_admin
call "%PS_EXE%" -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%SAFE_SCRIPT_DIR%\%APP_FILE%' -ArgumentList '%ARGS%' -Verb RunAs"
exit

endlocal
pause