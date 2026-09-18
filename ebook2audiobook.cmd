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
set "PS_ARGS=-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass"

"%PS_EXE%" %PS_ARGS% -Command "if ($ExecutionContext.SessionState.LanguageMode -ne 'FullLanguage') { exit 99 }"
if errorlevel 99 (
	echo ERROR: PowerShell Constrained Language Mode detected. This environment is not supported.
	goto :failed
)

"%PS_EXE%" %PS_ARGS% -Command "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8" >nul 2>&1

reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if errorlevel 1 (
	reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
)

for /f "delims=" %%e in ('cmd /c ""%PS_EXE%" %PS_ARGS% -Command "[char]27""') do set "ESC=%%e"

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
set "PYTHON_ENV=python_env"

:: Default PY_CMD to system python. NATIVE mode will override this in :check_uv.
:: BUILD_DOCKER and FULL_DOCKER will keep this default to use host/container python.
set "PY_CMD=python"

set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="
set "HOST_PROGRAMS=cmake rustup calibre ffmpeg-shared mediainfo nodejs espeak-ng sox tesseract"
set "DOCKER_PROGRAMS=curl ffmpeg mediainfo nodejs espeak-ng sox tesseract-ocr"
set "DOCKER_CALIBRE_INSTALLER_URL=https://download.calibre-ebook.com/linux-installer.sh"
set "DOCKER_WSL_CONTAINER=Debian"
set "DOCKER_MODE="
set "DOCKER_IMG_NAME=athomasson2/%APP_NAME%"
set "DOCKER_DEVICE_STR="
set "DEVICE_INFO_STR="
set "TMP=%SAFE_SCRIPT_DIR%\run"
set "TEMP=%SAFE_SCRIPT_DIR%\run"
if not exist "%TMP%" mkdir "%TMP%" >nul 2>&1

set "UV_INSTALL_DIR=%SAFE_USERPROFILE%\.local\bin"
set "UV_INSTALLER_PS1=https://astral.sh/uv/install.ps1"
set "SCOOP_HOME=%SAFE_USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "NODE_PATH=%SCOOP_HOME%\apps\nodejs\current"
set "TESSDATA_PREFIX=%SAFE_SCRIPT_DIR%\models\tessdata"
set "TESSDATA_BASE_URL=https://github.com/tesseract-ocr/tessdata_best/raw/main"
set "FFMPEG_BIN=%USERPROFILE%\scoop\apps\ffmpeg-shared\current\bin"
set "PATH=%UV_INSTALL_DIR%;%SCOOP_SHIMS%;%SCOOP_APPS%;%NODE_PATH%;%FFMPEG_BIN%;%PATH%"
set "INSTALLED_LOG=%SAFE_SCRIPT_DIR%\.installed"
set "UNINSTALLER=%SAFE_SCRIPT_DIR%\uninstall.cmd"
set "BROWSER_HELPER=%SAFE_SCRIPT_DIR%\.bh.ps1"
set "HEADLESS_FOUND=%ARGS:--headless=%"
set "DOCKER_IN_WSL=0"
set "DOCKER_DESKTOP=0"
set "PODMAN_DESKTOP=0"
IF NOT DEFINED DEVICE_TAG SET "DEVICE_TAG="
set "missing_prog_array="

for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
	set "PATH=%%B;%PATH%"
)

if "%ARCH%"=="X86" (
	echo %ESC%[31m=============== Error: 32-bit architecture is not supported.%ESC%[0m
	goto :failed
)

cd /d "%SAFE_SCRIPT_DIR%"
for /f "tokens=1* delims==" %%A in ('set arguments. 2^>nul') do set "%%A="

if not "%~1"=="" (
	setlocal EnableDelayedExpansion
	call :check_python
	for /f "delims=" %%V in ('%PY_CMD% -c "from lib.conf import cli_options; print(' '.join(cli_options))"') do set "VALID_ARGS=%%V"
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
if "%~1"=="" goto :parse_args_done
set "arg=%~1"
if "%arg:~0,2%"=="--" (
	set "key=%arg:~2%"
	if not "%~2"=="" (
		echo %~2 | findstr "^--" >nul
		if errorlevel 1 (
			set "temp_val=%~2"
			call set "arguments.%%key%%=!temp_val!"
			shift
			shift
			goto parse_args
		)
	)
	call set "arguments.%%key%%=true"
	shift
	goto parse_args
)
shift
goto parse_args

:parse_args_done

if defined arguments.script_mode (
	set "script_mode_valid=0"
	if /i "%arguments.script_mode%"=="%BUILD_DOCKER%" set "script_mode_valid=1"
	if /i "%arguments.script_mode%"=="%FULL_DOCKER%" set "script_mode_valid=1"
	if /i "%arguments.script_mode%"=="%NATIVE%" set "script_mode_valid=1"
)
if defined arguments.script_mode if "%script_mode_valid%"=="1" (
	set "SCRIPT_MODE=%arguments.script_mode%"
)
if defined arguments.script_mode if "%script_mode_valid%"=="0" (
	echo Error: Invalid script mode argument: %arguments.script_mode%
	goto :failed
)

if defined arguments.docker_device (
	if /i "%arguments.docker_device%"=="true" ( echo Error: --docker_device has no value & goto :failed )
	set "DOCKER_DEVICE_STR=%arguments.docker_device%"
)

if defined arguments.docker_mode (
	if not "%arguments.docker_mode%"=="podman" (
		if not "%arguments.docker_mode%"=="compose" (
			if /i "%arguments.docker_mode%"=="true" ( echo Error: --docker_mode has no value ) else ( echo Error: --docker_mode accepts only podman or compose as value )
			goto :failed
		)
	)
	set "DOCKER_MODE=%arguments.docker_mode%"
)

if defined arguments.script_mode (
	if /i "%arguments.script_mode%"=="true" ( echo Error: --script_mode requires a value & goto :failed )
	if /i not "%arguments.script_mode%"=="FULL_DOCKER" (
		setlocal enabledelayedexpansion
		for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do (
			set "argname=%%A"
			set "argname=!argname:arguments.=!"
			if not "!argname!"=="" (
				if /i not "!argname!"=="script_mode" if /i not "!argname!"=="docker_device" if /i not "!argname!"=="docker_mode" (
					echo Error: when --script_mode is not FULL_DOCKER, only --docker_device or --docker_mode are allowed. Invalid: --!argname!
					goto :failed
				)
			)
		)
		endlocal
	)
)

if not exist "%INSTALLED_LOG%" if /i not "%SCRIPT_MODE%"=="%BUILD_DOCKER%" ( type nul > "%INSTALLED_LOG%" )

if defined arguments.headless (
	if /i "%arguments.headless%"=="false" (
		setlocal enabledelayedexpansion
		for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do (
			set "argname=%%A"
			set "argname=!argname:arguments.=!"
			if not "!argname!"=="" if /i not "!argname!"=="headless" if /i not "!argname!"=="script_mode" if /i not "!argname!"=="share" (
				echo Error: In non-headless mode only --share option is allowed. Invalid: --!argname!
				goto :failed
			)
		)
		endlocal
	)
)

if defined arguments.share if defined arguments.headless if /i "%arguments.headless%"=="true" ( echo Error: --share option is only allowed in non-headless mode & goto :failed )
if defined arguments.version ( echo v%APP_VERSION% & goto :eof )
goto :main

:make_shortcut
set "shortcut=%~1"
"%PS_EXE%" %PS_ARGS% -Command "$q=[char]34; $s=New-Object -ComObject WScript.Shell; $sc=$s.CreateShortcut('%shortcut%'); $sc.TargetPath='cmd.exe'; $sc.Arguments='/k '+$q+$q+'cd /d '+$q+$env:SAFE_SCRIPT_DIR+$q+' && '+$q+$env:APP_FILE+$q+$q; $sc.WorkingDirectory=$env:SAFE_SCRIPT_DIR; $sc.IconLocation=$env:ICON_PATH; $sc.Save()"
exit /b

:build_gui
if /i not "%HEADLESS_FOUND%"=="%ARGS%" (
	if not exist "%STARTMENU_DIR%" mkdir "%STARTMENU_DIR%"
	if not exist "%STARTMENU_LNK%" ( call :make_shortcut "%STARTMENU_LNK%" & call :make_shortcut "%DESKTOP_LNK%" )
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayName" /d "%APP_NAME%" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayVersion" /d "%APP_VERSION%" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "UninstallString" /d "\"%UNINSTALLER%\"" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayIcon" /d "%ICON_PATH%" /f >nul 2>&1
	start "%APP_NAME%" /min "%PS_EXE%" %PS_ARGS% -File "%BROWSER_HELPER%" -HostName "%TEST_HOST%" -Port %TEST_PORT%
)
exit /b 0

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
if errorlevel 1 ( echo Python is not installed. & exit /b 1 )
exit /b 0

:check_scoop
where.exe /Q scoop >nul 2>&1
if errorlevel 1 ( echo Scoop is not installed. & exit /b 1 )
exit /b 0

:check_scoop_buckets
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket list" > "%TEMP%\scoop_buckets.txt" 2>&1
set "_MISSING_BUCKETS="
findstr /i "muggle" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! muggle"
findstr /i "extras" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! extras"
findstr /i "versions" "%TEMP%\scoop_buckets.txt" >nul 2>&1 || set "_MISSING_BUCKETS=!_MISSING_BUCKETS! versions"
del "%TEMP%\scoop_buckets.txt" >nul 2>&1
if defined _MISSING_BUCKETS ( exit /b 1 )
exit /b 0

:check_programs
setlocal EnableDelayedExpansion
for %%p in (%HOST_PROGRAMS%) do (
	set "prog=%%p"
	set "_found=0"
	if "%%p"=="nodejs" set "prog=node"
	if "%%p"=="calibre" set "prog=ebook-convert"
	if "%%p"=="ffmpeg-shared" set "prog=ffmpeg"
	if "%%p"=="rustup" ( if exist "%SAFE_USERPROFILE%\scoop\apps\rustup\current\.cargo\bin\rustup.exe" set "_found=1" )
	if "!_found!"=="0" (
		where.exe /Q !prog! >nul 2>&1
		if errorlevel 1 ( set "missing_prog_array=!missing_prog_array! %%p" )
	)
)
endlocal & set "missing_prog_array=%missing_prog_array%"
if not "%missing_prog_array%"=="" exit /b 1
exit /b 0

:install_scoop
echo Installing Scoop…
call "%PS_EXE%" %PS_ARGS% -Command "irm get.scoop.sh -OutFile '%TEMP%\install_scoop.ps1'"
call "%PS_EXE%" %PS_ARGS% -File "%TEMP%\install_scoop.ps1" -RunAsAdmin
del "%TEMP%\install_scoop.ps1" >nul 2>&1
if errorlevel 1 ( net session >nul 2>&1 & if not errorlevel 1 ( goto :restart_script ) & goto :failed )
findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
if errorlevel 1 echo scoop>>"%INSTALLED_LOG%"
call "%PS_EXE%" %PS_ARGS% -Command "scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git; scoop bucket add extras; scoop bucket add versions"
goto :restart_script

:install_scoop_buckets
call "%PS_EXE%" %PS_ARGS% -Command "$WarningPreference='SilentlyContinue'; scoop install git; scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git; scoop bucket add extras; scoop bucket add versions"
exit /b 0

:install_wsl
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	echo WSL2 is required to build Linux containers.
	pause
	wsl --unregister %DOCKER_WSL_CONTAINER% >nul 2>&1
	wsl --update
	wsl --install -d %DOCKER_WSL_CONTAINER% --no-launch
	wsl --shutdown
	timeout /t 3 /nobreak >nul
	wsl --user root -- echo "%DOCKER_WSL_CONTAINER% OK" >nul 2>&1
	if errorlevel 1 goto :failed
	echo [wsl2] > "%USERPROFILE%\.wslconfig"
	echo memory=4GB >> "%USERPROFILE%\.wslconfig"
	wsl --shutdown
)
goto :restart_script

:install_docker
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "apt-get update && apt-get install -y curl && curl -fsSL https://get.docker.com | SKIP_SLEEP=1 sh"
	if errorlevel 1 goto :failed
	wsl --user root -d %DOCKER_WSL_CONTAINER% -- bash -c "echo '[boot]' > /etc/wsl.conf && echo 'systemd=true' >> /etc/wsl.conf"
	wsl --shutdown
)
goto :restart_script

:install_uv
if not "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	echo Installing uv…
	call "%PS_EXE%" %PS_ARGS% -Command "irm %UV_INSTALLER_PS1% | iex"
	set "PATH=%UV_INSTALL_DIR%;%PATH%"
	where.exe /Q uv
	if errorlevel 1 goto :failed
	findstr /i /x "uv" "%INSTALLED_LOG%" >nul 2>&1
	if errorlevel 1 echo uv>>"%INSTALLED_LOG%"
)
goto :restart_script

:install_programs
echo Installing missing programs…
setlocal EnableDelayedExpansion
for %%p in (%missing_prog_array%) do (
	call "%PS_EXE%" %PS_ARGS% -Command "scoop install %%p"
	where.exe /Q %%p >nul 2>&1
	if errorlevel 1 goto :failed
)
endlocal & set "PATH=%PATH%"
set "missing_prog_array="
goto :main

:check_uv
where.exe /Q uv
if errorlevel 1 ( echo uv is not installed. & exit /b 1 )

set "CURRENT_ENV="
if defined VIRTUAL_ENV ( set "CURRENT_ENV=%VIRTUAL_ENV%" )
if defined CURRENT_ENV (
	if /i not "%CURRENT_ENV%"=="%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" (
		echo Current python virtual environment detected: %CURRENT_ENV%.
		echo This script runs with its own virtual env and must be out of any other virtual environment.
		exit /b 2
	)
)

:: Unconditionally lock PY_CMD to the venv for NATIVE mode
set "VIRTUAL_ENV=%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"
set "PY_CMD=%SAFE_SCRIPT_DIR%\%PYTHON_ENV%\Scripts\python.exe"

:: Let uv validate python_env
if exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" (
	if not exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%\pyvenv.cfg" (
		echo %PYTHON_ENV% is not a virtualenv — removing...
		rmdir /s /q "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
	) else (
		uv venv "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" --python %PYTHON_VERSION% --allow-existing >nul 2>&1
		if errorlevel 1 (
			echo %PYTHON_ENV% is inconsistent — removing and recreating...
			rmdir /s /q "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%"
		)
	)
)

if not exist "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" (
	echo Creating ./%PYTHON_ENV% with python %PYTHON_VERSION% via uv...
	uv python find %PYTHON_VERSION% >nul 2>&1
	if errorlevel 1 (
		uv python install %PYTHON_VERSION%
		if errorlevel 1 exit /b 3
	)
	uv venv "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%" --python %PYTHON_VERSION%
	if errorlevel 1 exit /b 3
	call :provision_env
	if errorlevel 1 exit /b 3
	> "%SAFE_SCRIPT_DIR%\%PYTHON_ENV%\.provisioned" echo %APP_VERSION%
)
exit /b 0

:provision_env
setlocal enabledelayedexpansion
set "RC=0"
call :check_device_info %SCRIPT_MODE%
if errorlevel 1 ( set "RC=1" & goto :provision_env_end )
call :install_device_packages
if errorlevel 1 ( set "RC=1" & goto :provision_env_end )
call :install_python_packages
if errorlevel 1 ( set "RC=1" & goto :provision_env_end )
:provision_env_end
endlocal & exit /b %RC%

:check_wsl
where.exe /Q wsl >nul 2>&1 || exit /b 1
for /f "delims=" %%a in ('wsl echo $WSL_DISTRO_NAME') do set "DOCKER_WSL_CONTAINER=%%a"
exit /b 0

:check_docker
if "%DOCKER_MODE%"=="podman" ( where.exe /Q podman-compose.exe >nul 2>&1 && set "PODMAN_DESKTOP=1" && exit /b 0 || exit /b 1 )
where.exe /Q docker.exe >nul 2>&1 && set "DOCKER_DESKTOP=1" && exit /b 0
wsl --user root -d %DOCKER_WSL_CONTAINER% -- which docker >nul 2>&1 || exit /b 1
exit /b 0

:check_docker_daemon
if "%PODMAN_DESKTOP%"=="1" exit /b 0
if "%DOCKER_DESKTOP%"=="1" ( docker info >nul 2>&1 && exit /b 0 || exit /b 1 )
wsl --user root -d %DOCKER_WSL_CONTAINER% -- docker info >nul 2>&1 && exit /b 0
wsl --user root -d %DOCKER_WSL_CONTAINER% -- service docker start >nul 2>&1
exit /b 0

:check_device_info
set "ARG=%~1"
set "DEVICE_INFO_STR="
for /f "delims=" %%I in ('"%PY_CMD%" -c "import sys; from lib.classes.device_installer import DeviceInstaller as D; print(D().check_device_info(sys.argv[1]))" "%ARG%"') do set "DEVICE_INFO_STR=%%I"
if not defined DEVICE_INFO_STR exit /b 1
exit /b 0

:json_get
setlocal enabledelayedexpansion
set "KEY=%~1"
set "JSON_VALUE="
for /f "delims=" %%i in ('powershell -Command "$env:DEVICE_INFO_STR | ConvertFrom-Json | Select-Object -ExpandProperty %KEY%"') do set "JSON_VALUE=%%i"
endlocal & set "DEVICE_TAG=%JSON_VALUE%"
exit /b 0

:install_device_packages
"%PS_EXE%" %PS_ARGS% -Command "& '%PY_CMD%' -c \"import sys, os; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_device_packages(os.environ.get('DEVICE_INFO_STR', '')))\""
exit /b %errorlevel%

:install_python_packages
echo Installing python dependencies…
"%PS_EXE%" %PS_ARGS% -Command "& '%PY_CMD%' -c \"import sys; from lib.classes.device_installer import DeviceInstaller; device = DeviceInstaller(); sys.exit(device.install_python_packages())\""
exit /b %errorlevel%

:check_sitecustomized
set "src_pyfile=%SAFE_SCRIPT_DIR%\components\sitecustomize.py"
set "site_packages_path="
"%PY_CMD%" -c "import sysconfig;print(sysconfig.get_paths()['purelib'])" > "%TEMP%\purelib.txt" 2>nul
set /p site_packages_path=<"%TEMP%\purelib.txt"
del "%TEMP%\purelib.txt" >nul 2>&1
if not defined site_packages_path exit /b 1
set "dst_pyfile=%site_packages_path%\sitecustomize.py"
if not exist "%dst_pyfile%" ( copy /y "%src_pyfile%" "%dst_pyfile%" >nul )
xcopy /d /y "%src_pyfile%" "%site_packages_path%\" >nul
exit /b 0

:build_docker_image
setlocal enabledelayedexpansion
set "ARG=%~1"
set "ARG_ESCAPED=%ARG:"=\"%"
set "DOCKER_IMG_NAME=%DOCKER_IMG_NAME%:%DEVICE_TAG%"
set "cmd_options="
set "py_vers=%PYTHON_VERSION%"
if /i "%DEVICE_TAG:~0,2%"=="cu" set "cmd_options=--gpus all"
if /i "%DEVICE_TAG:~0,4%"=="rocm" set "cmd_options=--device=/dev/kfd --device=/dev/dri"
if /i "%DEVICE_TAG%"=="xpu" set "cmd_options=--device=/dev/dri"

if /i "%DEVICE_TAG%"=="cpu" set "COMPOSE_PROFILES=cpu"
if /i "%DEVICE_TAG:~0,2%"=="cu" set "COMPOSE_PROFILES=cuda"
if /i "%DEVICE_TAG:~0,4%"=="rocm" set "COMPOSE_PROFILES=rocm"
if /i "%DEVICE_TAG%"=="xpu" set "COMPOSE_PROFILES=xpu"

if "%DOCKER_MODE%"=="podman" (
	podman build --format docker --no-cache --network=host --build-arg PYTHON_VERSION="%py_vers%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%" -t "%DOCKER_IMG_NAME%" -f Dockerfile .
) else if "%DOCKER_MODE%"=="compose" (
	docker compose --profile "%COMPOSE_PROFILES%" build --no-cache --build-arg PYTHON_VERSION="%py_vers%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%"
) else (
	docker build --no-cache --build-arg PYTHON_VERSION="%py_vers%" --build-arg DEVICE_TAG="%DEVICE_TAG%" --build-arg DOCKER_DEVICE_STR="%ARG_ESCAPED%" -t "%DOCKER_IMG_NAME%" .
)
endlocal
exit /b 0

:main
if defined arguments.help (
	if /i "%arguments.help%"=="true" (
		call :check_python
		call "%PY_CMD%" -u "%SAFE_SCRIPT_DIR%\app.py" %ARGS%
		goto :eof
	)
) else (
	if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
		if "%DOCKER_DEVICE_STR%"=="" (
			call :check_python
			call :check_wsl
			call :check_docker
			call :check_docker_daemon
			call :check_device_info %SCRIPT_MODE%
			call :install_device_packages
			if "%DEVICE_TAG%"=="" call :json_get tag
			call :build_docker_image "%DEVICE_INFO_STR%"
		)
	) else if "%SCRIPT_MODE%"=="%NATIVE%" (
		call :check_scoop || goto :install_scoop
		call :check_scoop_buckets || goto :install_scoop_buckets
		call :check_programs || goto :install_programs
		call :check_uv
		call :check_sitecustomized
		call :build_gui
		call uv run --no-project -- "%PY_CMD%" -u "%SAFE_SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
	) else if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
		call :check_sitecustomized
		call "%PY_CMD%" -u "%SAFE_SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
	)
)
goto :eof

:failed
echo =============== ebook2audiobook is not correctly installed.
exit /b 1

:restart_script
start "%APP_NAME%" cmd /k "cd /d "%SAFE_SCRIPT_DIR%" & call %APP_FILE% %ARGS%"
exit 0

endlocal
pause