@echo off
setlocal enabledelayedexpansion

:: Capture all arguments into ARGS
set "ARGS=%*"

set "NATIVE=native"
set "FULL_DOCKER=full_docker"

set "SCRIPT_MODE=%NATIVE%"
set "SCRIPT_DIR=%~dp0"

set "PYTHON_VERSION=3.12"
set "PYTHON_ENV=python_env"
set "CURRENT_ENV="
set "PROGRAMS_LIST=calibre ffmpeg nodejs espeak-ng"

set "TMP=%SCRIPT_DIR%\tmp"
set "TEMP=%SCRIPT_DIR%\tmp"
set "ESPEAK_DATA_PATH=%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data"
set "PATH=%USERPROFILE%\scoop\shims;%CONDA_PATH%;%CONDA_INSTALL_DIR%\condabin;%PATH%"

set "PROGRAMS_CHECK=0"
set "CONDA_CHECK_STATUS=0"
set "CONDA_RUN_INIT=0"
set "DOCKER_CHECK_STATUS=0"

set "HELP_FOUND=%ARGS:--help=%"

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "PATH=%%B;%PATH%"
)

cd /d "%SCRIPT_DIR%"

:: Check if running inside Docker
if defined CONTAINER (
	echo Running in %FULL_DOCKER% mode
	set "SCRIPT_MODE=%FULL_DOCKER%"
	goto main
)

echo Running in %SCRIPT_MODE% mode
goto conda_check

:conda_check
set "conda_version="
where /Q conda
if %errorlevel% neq 0 (
	call rmdir /s /q "%CONDA_INSTALL_DIR%" 2>nul
	set "CONDA_CHECK_STATUS=1"
) else (
		:: Check if running in a Conda environment
		if defined CONDA_DEFAULT_ENV (
			set "CURRENT_ENV=%CONDA_PREFIX%"
		)
		:: Check if running in a Python virtual environment
		if defined VIRTUAL_ENV (
			set "CURRENT_ENV=%VIRTUAL_ENV%"
		)
		for /f "delims=" %%i in ('where /Q python') do (
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
		if not "%CURRENT_ENV%"=="" (
			echo Current python virtual environment detected: %CURRENT_ENV%. 
			echo This script runs with its own virtual env and must be out of any other virtual environment when it's launched.
			goto failed
		)
		call :programs_check
)
goto dispatch

:programs_check
set "missing_prog_array="
for %%p in (%PROGRAMS_LIST%) do (
    set "prog=%%p"
    if "%%p"=="nodejs" set "prog=node"
    where /Q !prog!
    if errorlevel 1 (
        echo %%p is not installed.
        set "missing_prog_array=!missing_prog_array! %%p"
    )
)
if not "!missing_prog_array!"=="" (
    set "PROGRAMS_CHECK=1"
    goto install_components
)
goto dispatch

:docker_check
where /Q docker
if %errorlevel% neq 0 (
	set "DOCKER_CHECK_STATUS=1"
) else (
	:: Verify Docker is running
	call docker info >nul 2>&1
	if %errorlevel% neq 0 (
		set "DOCKER_CHECK_STATUS=1"
	) else (
		goto dispatch
	)
)
goto install_components

:install_components
:: Install Scoop if not already installed
where /Q scoop
if %errorlevel% neq 0 (
    echo Scoop is not installed. Installing Scoop...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -useb get.scoop.sh | iex"  
	call refreshenv
    call scoop install git
    call scoop bucket add extras
    call scoop bucket known
)

:: Install missing packages if any
if not "%PROGRAMS_CHECK%"=="0" (
	echo Installing %missing_prog_array%
	call scoop install %missing_prog_array%
	set "PROGRAMS_CHECK=0"
	set "missing_prog_array="
)
:: Install Conda if not already installed
if not "%CONDA_CHECK_STATUS%"=="0" (	
	echo Installing Conda...
	call scoop install miniconda3
	echo Conda installed successfully.
	set "CONDA_RUN_INIT=1"
	set "CONDA_CHECK_STATUS=0"
)
:: Install Docker if not already installed
if not "%DOCKER_CHECK_STATUS%"=="0" (
	echo Docker is not installed. Installing it now...
	call scoop install docker-cli
	call scoop install docker-engine
	call where /Q docker
	if %errorlevel% equ 0 (
		echo Starting Docker Engine...
		net start com.docker.service >nul 2>&1
		if %errorlevel% equ 0 (
			echo Docker installed and started successfully.
			set "DOCKER_CHECK_STATUS=0"
		) 
	)
)
goto dispatch

:dispatch
if "%PROGRAMS_CHECK%"=="0" (
	if "%CONDA_CHECK_STATUS%"=="0" (
		if "%DOCKER_CHECK_STATUS%"=="0" (
			goto main
		) else (
			goto failed
		)
	)
)
echo PROGRAMS_CHECK: %PROGRAMS_CHECK%
echo CONDA_CHECK_STATUS: %CONDA_CHECK_STATUS%
echo DOCKER_CHECK_STATUS: %DOCKER_CHECK_STATUS%
timeout /t 5 /nobreak >nul
goto install_components

:main
if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
	call python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
) else (
	if "%CONDA_RUN_INIT%"=="1" (
		call conda init
		set "CONDA_RUN_INIT=0"
	)
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
		call python -m pip cache purge
		call python -m pip install --upgrade pip
		for /f %%p in (requirements.txt) do (
			echo Installing %%p...
			python -m pip install --upgrade --no-cache-dir --progress-bar=on %%p
		)
		echo ✅ All required packages are installed.
	) else (
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
	)
	call python "%SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
	call conda deactivate
)
exit /b

:failed
echo ebook2audiobook is not correctly installed or run.
exit /b

endlocal
pause
