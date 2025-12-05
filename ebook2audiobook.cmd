@echo off

setlocal enabledelayedexpansion

:: Enable ANSI VT mode
reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if errorlevel 1 (
	reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul
)

:: Real ESC byte via PowerShell (RELIABLE)
for /f "delims=" %%e in ('powershell -NoLogo -NoProfile -Command "[char]27"') do set "ESC=%%e"

:: Capture all arguments into ARGS
set "ARGS=%*"
set "NATIVE=native"
set "BUILD_DOCKER=build_docker"
set "SCRIPT_MODE=%NATIVE%"
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "APP_NAME=ebook2audiobook"
set /p APP_VERSION=<"%SCRIPT_DIR%\VERSION.txt"
set "APP_FILE=%APP_NAME%.cmd"
set "OS_LANG=%LANG%"& if "!OS_LANG!"=="" set "OS_LANG=en"& set "OS_LANG=!OS_LANG:~0,2!"
set "TEST_HOST=127.0.0.1"
set "TEST_PORT=7860"
set "ICON_PATH=%SCRIPT_DIR%\tools\icons\windows\appIcon.ico"
set "STARTMENU_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\%APP_NAME%"
set "STARTMENU_LNK=%STARTMENU_DIR%\%APP_NAME%.lnk"
set "DESKTOP_LNK=%USERPROFILE%\Desktop\%APP_NAME%.lnk"
set "ARCH=%PROCESSOR_ARCHITECTURE%"
set "PYTHON_VERSION=3.12"
set "PYTHON_SCOOP=python%PYTHON_VERSION:.=%"
set "PYTHON_ENV=python_env"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="
set "HOST_PROGRAMS=rustup python calibre-normal ffmpeg nodejs espeak-ng sox tesseract"
set "DOCKER_PROGRAMS=curl ffmpeg nodejs espeak-ng sox tesseract-ocr"
set "DOCKER_CALIBRE_INSTALLER_URL=https://download.calibre-ebook.com/linux-installer.sh"
set "DOCKER_DEVICE_STR="
set "DOCKER_IMG_NAME=ebook2audiobook"
set "TMP=%SCRIPT_DIR%\tmp"
set "TEMP=%SCRIPT_DIR%\tmp"
set "ESPEAK_DATA_PATH=%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data"
set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
set "CONDA_HOME=%USERPROFILE%\Miniforge3"
set "CONDA_INSTALLER=Miniforge3-Windows-x86_64.exe"
set "CONDA_ENV=%CONDA_HOME%\condabin\conda.bat"
set "CONDA_PATH=%CONDA_HOME%\condabin"
set "TESSDATA_PREFIX=%SCRIPT_DIR%\models\tessdata"
set "NODE_PATH=%SCOOP_HOME%\apps\nodejs\current"
set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%;%PATH%"
set "INSTALLED_LOG=%SCRIPT_DIR%\.installed"
set "UNINSTALLER=%SCRIPT_DIR%\uninstall.cmd"
set "BROWSER_HELPER=%SCRIPT_DIR%\.bh.ps1"
set "HELP_FOUND=%ARGS:--help=%"
set "HEADLESS_FOUND=%ARGS:--headless=%"

set "OK_SCOOP=0"
set "OK_CONDA=0"
set "OK_PROGRAMS=0"
set "OK_DOCKER=0"

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
	set "PATH=%%B;%PATH%"
)

if "%ARCH%"=="x86" (
	echo %ESC%[31m=============== Error: 32-bit architecture is not supported.%ESC%[0m
	goto :failed
)

if not exist "%INSTALLED_LOG%" (
	type nul > "%INSTALLED_LOG%"
)

cd /d "%SCRIPT_DIR%"

:: Clear previous associative values
for /f "tokens=1* delims==" %%A in ('set arguments. 2^>nul') do set "%%A="
set "FORWARD_ARGS="

::::::::::::::::::::::::::::::: CORE FUNCTIONS

:parse_args
if "%~1"=="" goto :parse_args_done
set "arg=%~1"
:: ALWAYS forward args
set "FORWARD_ARGS=!FORWARD_ARGS! !arg!"
:: Flag or key-value argument
if "!arg:~0,2!"=="--" (
	set "key=!arg:~2!"
	:: Check for a value (next arg exists AND does not start with --)
	if not "%~2"=="" (
		echo %~2 | findstr "^--" >nul
		if errorlevel 1 (
			set "arguments.!key!=%~2"
			shift & shift
			goto parse_args
		)
	)
	:: Boolean flag
	set "arguments.!key!=true"
	shift
	goto parse_args
)
shift
goto parse_args

:parse_args_done
if defined arguments.script_mode (
	if /I "!arguments.script_mode!"=="%BUILD_DOCKER%" (
		set "SCRIPT_MODE=!arguments.script_mode!"
	) else (
		echo Error: Invalid script mode argument: !arguments.script_mode!
		goto :failed
	)
)
if defined arguments.docker_device (
	set "DOCKER_DEVICE_STR=!arguments.docker_device!"
	if /i "!arguments.docker_device!"=="true" (
		echo Error: --docker_device has no value!
		goto :failed
	)
)
if defined arguments.script_mode (
	if /I "!arguments.script_mode!"=="true" (
		echo Error: --script_mode requires a value
		goto :failed
	)
	for /f "tokens=1,2 delims==" %%A in ('set arguments. 2^>nul') do (
		set "argname=%%A"
		set "argname=!argname:arguments.=!"
		if /I not "!argname!"=="script_mode" if /I not "!argname!"=="docker_device" (
			echo Error: when --script_mode is used, only --docker_device is allowed as additional option. Invalid option: --!argname!
			goto :failed
		)
	)
)
if defined arguments.docker_device (
	if /I "!arguments.docker_device!"=="true" (
		echo Error: --docker_device requires a value
		goto :failed
	)
)
goto :check_scoop

::::::::::::::: DESKTOP APP
:make_shortcut
set "shortcut=%~1"
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command ^
  "$s = New-Object -ComObject WScript.Shell; " ^
  "$sc = $s.CreateShortcut('%shortcut%'); " ^
  "$sc.TargetPath = 'cmd.exe'; " ^
  "$sc.Arguments = '/k ""cd /d """"%SCRIPT_DIR%"""" && """"%APP_FILE%""""""'; " ^
  "$sc.WorkingDirectory = '%SCRIPT_DIR%'; " ^
  "$sc.IconLocation = '%ICON_PATH%'; " ^
  "$sc.Save()"
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
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "InstallLocation" /d "%SCRIPT_DIR%" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "UninstallString" /d "\"%UNINSTALLER%\"" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "DisplayIcon" /d "%ICON_PATH%" /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "NoModify" /t REG_DWORD /d 1 /f >nul 2>&1
	reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\%APP_NAME%" /v "NoRepair" /t REG_DWORD /d 1 /f >nul 2>&1
	start "%APP_NAME%" powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%BROWSER_HELPER%" -HostName "%TEST_HOST%" -Port %TEST_PORT%
)
exit /b
:::::: END OF DESKTOP APP

:get_iso3_lang
set "arg=%~1"
if /i "%arg%"=="en"  echo eng& goto :eof
if /i "%arg%"=="fr"  echo fra& goto :eof
if /i "%arg%"=="de"  echo deu& goto :eof
if /i "%arg%"=="it"  echo ita& goto :eof
if /i "%arg%"=="es"  echo spa& goto :eof
if /i "%arg%"=="pt"  echo por& goto :eof
if /i "%arg%"=="ar"  echo ara& goto :eof
if /i "%arg%"=="tr"  echo tur& goto :eof
if /i "%arg%"=="ru"  echo rus& goto :eof
if /i "%arg%"=="bn"  echo ben& goto :eof
if /i "%arg%"=="zh"  echo chi_sim& goto :eof
if /i "%arg%"=="fa"  echo fas& goto :eof
if /i "%arg%"=="hi"  echo hin& goto :eof
if /i "%arg%"=="hu"  echo hun& goto :eof
if /i "%arg%"=="id"  echo ind& goto :eof
if /i "%arg%"=="jv"  echo jav& goto :eof
if /i "%arg%"=="ja"  echo jpn& goto :eof
if /i "%arg%"=="ko"  echo kor& goto :eof
if /i "%arg%"=="pl"  echo pol& goto :eof
if /i "%arg%"=="ta"  echo tam& goto :eof
if /i "%arg%"=="te"  echo tel& goto :eof
if /i "%arg%"=="yo"  echo yor& goto :eof
echo eng
exit /b

:check_scoop
where /Q scoop
if errorlevel 1 (
	echo Scoop is not installed.
	set "OK_SCOOP=1"
	goto :install_programs
)
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	goto :check_required_programs
) else (
	goto :check_conda
)
exit /b

:check_required_programs
set "missing_prog_array="
for %%p in (%HOST_PROGRAMS%) do (
	set "prog=%%p"
	if "%%p"=="nodejs" set "prog=node"
	if "%%p"=="calibre-normal" set "prog=calibre"
	where /Q !prog!
	if errorlevel 1 (
		echo %%p is not installed.
		set "missing_prog_array=!missing_prog_array! %%p"
	)
)
if not "%missing_prog_array%"=="" (
	set "OK_PROGRAMS=1"
	goto :install_programs
)
goto :dispatch
exit /b

:install_programs
if not "%OK_SCOOP%"=="0" (
	echo Installing Scoop...
	call powershell -command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser"
	call powershell -command "iwr -useb get.scoop.sh | iex"
	where /Q scoop
	if not errorlevel 1 (
		call scoop install git
		call scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git
		call scoop bucket add extras
		call scoop bucket add versions
		if "%OK_PROGRAMS%"=="0" (
			echo %ESC%[32m=============== Scoop is installed! ===============%ESC%[0m
			set "OK_SCOOP=0"
		)
		findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo scoop>>"%INSTALLED_LOG%"
		)
		start "" cmd /k cd /d "%SCRIPT_DIR%" ^& call "%~f0"
	) else (
		echo %ESC%[31m=============== Scoop installation failed.%ESC%[0m
		goto :failed
	)
	exit
)
if not "%OK_CONDA%"=="0" (
	echo Installing Miniforge...
	call powershell -Command "Invoke-WebRequest -Uri %CONDA_URL% -OutFile "%CONDA_INSTALLER%"
	call start /wait "" "%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniforge3
	where /Q conda
	if not errorlevel 1 (
		echo %ESC%[32m=============== Miniforge3 is installed! ===============%ESC%[0m
		findstr /i /x "Miniforge3" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo Miniforge3>>"%INSTALLED_LOG%"
		)
	) else (
		echo %ESC%[31m=============== Miniforge3 installation failed.%ESC%[0m
		goto :failed
	)
	if not exist "%USERPROFILE%\.condarc" (
		call conda config --set auto_activate false
	)
	call conda update --all -y
	call conda clean --index-cache -y
	call conda clean --packages --tarballs -y
	del "%CONDA_INSTALLER%"
	set "OK_CONDA=0"
	start "" cmd /k cd /d "%CD%" ^& call "%~f0"
	exit
)
if not "%OK_PROGRAMS%"=="0" (
	echo Installing missing programs...
	if "%OK_SCOOP%"=="0" (
		call scoop bucket add muggle b https://github.com/hu3rror/scoop-muggle.git
		call scoop bucket add extras
		call scoop bucket add versions
	)
	for %%p in (%missing_prog_array%) do (
		set "prog=%%p"
		call scoop install %%p
		if "%%p"=="tesseract" (
			where /Q !prog!
			if not errorlevel 1 (
				for /f %%i in ('call :get_iso3_lang %OS_LANG%') do set "tesslang=%%i"
				echo Detected system language: !OS_LANG! → downloading OCR language: !tesslang!
				set "tessdata=%SCOOP_APPS%\tesseract\current\tessdata"
				if not exist "!tessdata!\!tesslang!.traineddata" (
					powershell -Command "Invoke-WebRequest -Uri https://github.com/tesseract-ocr/tessdata_best/raw/main/!tesslang!.traineddata -OutFile '!tessdata!\!tesslang!.traineddata'"
				)
				if exist "!tessdata!\!tesslang!.traineddata" (
					echo Tesseract OCR language !tesslang! installed in !tessdata!
				) else (
					echo Failed to install OCR language !tesslang!
				)
			)
		)
		if "%%p"=="nodejs" (
			set "prog=node"
		) else (
			if "%%p"=="calibre-normal" (
				set "prog=calibre"
			)
		)
		if "%%p"=="rustup" (
			if exist "%USERPROFILE%\scoop\apps\rustup\current\.cargo\bin\rustup.exe" (
				set "PATH=%USERPROFILE%\scoop\apps\rustup\current\.cargo\bin;%PATH%"
			)
		)
		where /Q !prog!
		if not errorlevel 1 (
			echo %ESC%[32m=============== %%p is installed! ===============%ESC%[0m
			findstr /i /x "%%p" "%INSTALLED_LOG%" >nul 2>&1
			if errorlevel 1 (
				echo %%p>>"%INSTALLED_LOG%"
			)
		) else (
			echo %ESC%[31m=============== %%p installation failed.%ESC%[0m
			goto :failed
		)
	)
	call powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%', 'User')"
	set "OK_SCOOP=0"
	set "OK_PROGRAMS=0"
	set "missing_prog_array="
)
goto :dispatch
exit /b

:check_conda
where /Q conda
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
for /f "delims=" %%i in ('where python') do (
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
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		echo Creating ./python_env version %PYTHON_ENV%...
		call "%CONDA_HOME%\Scripts\activate.bat"
		call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
		call conda update --all -y
		call conda clean --index-cache -y
		call conda clean --packages --tarballs -y
		call conda activate base
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
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
exit /b 0

:check_docker
where /Q docker
if errorlevel 1 (
	echo %ESC%[31m=============== Docker is not installed or not running. Please install or run Docker manually.%ESC%[0m
	exit /b 1
)
exit /b 0

:compare_versions
setlocal EnableDelayedExpansion
set "v1=%~1"
set "v2=%~2"
:: Remove dots
set "v1_n=%v1:.=%"
set "v2_n=%v2:.=%"
:: Pad with zeros
set "v1_n=000000%v1_n%"
set "v2_n=000000%v2_n%"
set "v1_n=!v1_n:~-6!"
set "v2_n=!v2_n:~-6!"
if !v1_n! LSS !v2_n! (endlocal & set cmp_result=LEQ & exit /b)
if !v1_n! EQU !v2_n! (endlocal & set cmp_result=LEQ & exit /b)
endlocal & set cmp_result=GTR & exit /b

:install_python_packages
echo [ebook2audiobook] Installing dependencies...
python -m pip cache purge >nul 2>&1
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade --no-cache-dir --progress-bar on --disable-pip-version-check --use-pep517 -r "%SCRIPT_DIR%\requirements.txt"
if errorlevel 1 goto :failed
for /f "tokens=2 delims=: " %%A in ('pip show torch 2^>nul ^| findstr /b /c:"Version"') do (
	set "torch_ver=%%A"
)
call :compare_versions "%torch_ver%" "2.2.2"
if /I "%cmp_result%"=="LEQ" (
	python -m pip install --upgrade --no-cache-dir --use-pep517 "numpy<2"
	if errorlevel 1 goto :failed
)
python -m unidic download
if errorlevel 1 goto :failed
echo [ebook2audiobook] Installation completed.
exit /b 0

:check_device_info
set "arg=%~1"
powershell -NoLogo -NoProfile -Command ^
@"
%PYTHON_SCOOP% - << 'EOF'
from lib.classes.device_installer import DeviceInstaller
device = DeviceInstaller()
result = device.check_device_info(r"%arg%")
if result:
	print(result)
	raise SystemExit(0)
raise SystemExit(1)
EOF
"@
exit /b %errorlevel%

:install_device_packages
set "arg=%~1"
powershell -NoLogo -NoProfile -Command ^
@"
python - << 'EOF'
import sys
from lib.classes.device_installer import DeviceInstaller
device = DeviceInstaller()
exit_code = device.install_device_packages(r"%arg%")
sys.exit(exit_code)
EOF
"@
exit /b %errorlevel%

:check_sitecustomized
set "src_pyfile=%SCRIPT_DIR%\components\sitecustomize.py"
for /f "delims=" %%a in ('python -c "import sysconfig;print(sysconfig.get_paths()[\"purelib\"])"') do (
	set "site_packages_path=%%a"
)
if "%site_packages_path%"=="" (
	echo [WARN] Could not detect Python site-packages
	exit /b 0
)
set "dst_pyfile=%site_packages_path%\sitecustomize.py"
if not exist "%dst_pyfile%" (
	copy /y "%src_pyfile%" "%dst_pyfile%" >nul
	if errorlevel 1 (
		echo %ESC%[31m=============== sitecustomize.py hook installation error: copy failed.%ESC%[0m
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
for /f %%A in ('powershell -NoLogo -Command "(ConvertFrom-Json ''%ARG%'').tag"') do set "TAG=%%A"
powershell -nologo -noprofile -command "if (!(Get-Command docker -ErrorAction SilentlyContinue)) { Write-Host '=============== Error: Docker must be installed and running!' -ForegroundColor Red; exit 1 }"
if errorlevel 1 exit /b 1
powershell -nologo -noprofile -command "if (docker compose version > $null 2>&1) { exit 0 } else { exit 1 }"
set "HAS_COMPOSE=%errorlevel%"
set "DOCKER_IMG_NAME=%DOCKER_IMG_NAME%:%TAG%"
if %HAS_COMPOSE%==0 (
	:: Use docker compose v2
	BUILD_NAME="%DOCKER_IMG_NAME%" docker compose --progress=plain build --no-cache ^
		--build-arg DOCKER_DEVICE_STR="%ARG%" ^
		--build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" ^
		--build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" ^
		--build-arg ISO3_LANG="%ISO3_LANG%"
	if errorlevel 1 exit /b 1
) else (
	:: Use docker build (fallback)
	docker build --no-cache --progress plain ^
		--build-arg DOCKER_DEVICE_STR="%ARG%" ^
		--build-arg DOCKER_PROGRAMS_STR="%DOCKER_PROGRAMS%" ^
		--build-arg CALIBRE_INSTALLER_URL="%DOCKER_CALIBRE_INSTALLER_URL%" ^
		--build-arg ISO3_LANG="%ISO3_LANG%" ^
		-t "%DOCKER_IMG_NAME%" .
	if errorlevel 1 exit /b 1
)
set "cmd_options="
if /i "%TAG%"=="cpu"      set "cmd_options="
if /i "%TAG:~0,2%"=="cu"  set "cmd_options=--gpus all"
if /i "%TAG%"=="mps"      set "cmd_options="
if /i "%TAG%"=="xpu"      set "cmd_options=--device=/dev/dri"
if /i "%TAG:~0,4%"=="rocm" set "cmd_options=--device=/dev/kfd --device=/dev/dri"
if /i "%TAG:~0,6%"=="jetson" set "cmd_options=--runtime nvidia"
echo Docker image ready! to run your docker: docker run %cmd_options% -it --rm -p 7860:7860 %DOCKER_IMG_NAME%
exit /b 0

:::::::::::: END CORE FUNCTIONS

:dispatch
if "%OK_SCOOP%"=="0" (
	if "%OK_PROGRAMS%"=="0" (
		if "%OK_CONDA%"=="0" (
			if "%OK_DOCKER%"=="0" (
				goto :main
			) else (
				goto :failed
			)
		)
	)
)
echo OK_PROGRAMS: %OK_PROGRAMS%
echo OK_CONDA: %OK_CONDA%
echo OK_DOCKER: %OK_DOCKER%
goto :install_programs
exit /b

:main
if defined arguments.help (
	if /I "!arguments.help!"=="true" (
		where /Q conda
		if errorlevel 0 (
			call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
			call python "%SCRIPT_DIR%\app.py" %FORWARD_ARGS%
			call conda deactivate
		) else (
			echo Ebook2Audiobook must be installed before to run --help.
		)
		goto :eof
	)
) else (
	if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
		if "!DOCKER_DEVICE_STR!"=="" (
			call %PYTHON_SCOOP% --version >null 2>&1 || call scoop install %PYTHON_SCOOP% 2>null
			where /Q %PYTHON_SCOOP%
			if errorlevel 1 (
				echo %ESC%[31m=============== %PYTHON_SCOOP% installation failed.%ESC%[0m
				goto :failed
			)
			call :check_docker
			if errorlevel 1 goto :failed
			call docker image inspect "%DOCKER_IMG_NAME%" >nul 2>&1
			if errorlevel 0 (
				echo [STOP] Docker image '%DOCKER_IMG_NAME%' already exists. Aborting build.
				echo Delete it using: docker rmi %DOCKER_IMG_NAME%
				goto :failed
			)
			call :check_device_info "%SCRIPT_MODE%"
			set "deviceinfo=%errorlevel%"
			if errorlevel 1 goto :failed
			call :build_docker_image "%deviceinfo%"
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
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
		call :check_sitecustomized
		if errorlevel 1 goto :failed
		call :build_gui
		call python "%SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
		call conda deactivate >nul && call conda deactivate >nul
	)
)
exit /b 0

:failed
echo =============== ebook2audiobook is not correctly installed.
where conda >nul 2>&1 && call conda deactivate >nul 2>&1 && call conda deactivate >nul
exit /b 1

endlocal
pause