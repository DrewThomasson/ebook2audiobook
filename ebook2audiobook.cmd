@echo off
setlocal enabledelayedexpansion

:: Capture all arguments into ARGS
set "ARGS=%*"

set "NATIVE=native"
set "DOCKER_UTILS=docker_utils"
set "FULL_DOCKER=full_docker"

set "SCRIPT_MODE=%NATIVE%"
set "SCRIPT_DIR=%~dp0"

set "PYTHON_VERSION=3.11"
set "DOCKER_UTILS_IMG=utils"
set "PYTHON_ENV=python_env"
set "CURRENT_ENV="
set "PROGRAMS_LIST=calibre ffmpeg"

set "CONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "CONDA_INSTALLER=%TEMP%\Miniconda3-latest-Windows-x86_64.exe"
set "CONDA_INSTALL_DIR=%USERPROFILE%\miniconda3"
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "PATH=%CONDA_PATH%;%PATH%"

set "PROGRAMS_CHECK=0"
set "CONDA_CHECK_STATUS=0"
set "DOCKER_CHECK_STATUS=0"
set "DOCKER_BUILD_STATUS=0"

for %%A in (%*) do (
	if "%%A"=="%DOCKER_UTILS%" (
		set "SCRIPT_MODE=%DOCKER_UTILS%"
		break
	)
)

cd /d "%SCRIPT_DIR%"

:: Check if running inside Docker
if defined CONTAINER (
	echo Running in %FULL_DOCKER% mode
	set "SCRIPT_MODE=%FULL_DOCKER%"
	goto main
)

echo Running in %SCRIPT_MODE% mode

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
if not "%CURRENT_ENV%"=="" (
	echo Current python virtual environment detected: %CURRENT_ENV%. 
	echo This script runs with its own virtual env and must be out of any other virtual environment when it's launched.
	goto failed
)
goto conda_check

:conda_check
where conda >nul 2>&1
if %errorlevel% neq 0 (
    set "CONDA_CHECK_STATUS=1"
) else (
    if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
        call :docker_check
    ) else (
        call :programs_check
    )
)
goto dispatch
exit /b

:programs_check
set "missing_prog_array="
for %%p in (%PROGRAMS_LIST%) do (
    set "FOUND="
    for /f "delims=" %%i in ('where %%p 2^>nul') do (
        set "FOUND=%%i"
    )
    if not defined FOUND (
        echo %%p is not installed.
        set "missing_prog_array=!missing_prog_array! %%p"
    )
)
if not "%missing_prog_array%"=="" (
	set "PROGRAMS_CHECK=1"
)
exit /b

:docker_check
docker --version >nul 2>&1
if %errorlevel% neq 0 (
	set "DOCKER_CHECK_STATUS=1"
) else (
	:: Verify Docker is running
	call docker info >nul 2>&1
	if %errorlevel% neq 0 (
		set "DOCKER_CHECK_STATUS=1"
	) else (
		:: Check if the Docker socket is running
		set "docker_socket="
		if exist \\.\pipe\docker_engine (
			set "docker_socket=Windows"
		)
		if not defined docker_socket (
			echo cannot connect to docker socket. Check if the docker socket is running.
			goto failed
		) else (
			:: Check if the Docker image is available
			call docker images -q %DOCKER_UTILS_IMG% >nul 2>&1
			if %errorlevel% neq 0 (
				echo Docker image '%DOCKER_UTILS_IMG%' not found. Installing it now...
				set "DOCKER_BUILD_STATUS=1"
			) else (
				goto dispatch
			)
		)
	)
)
goto install_components
exit /b

:install_components
:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
	echo This script needs to be run as administrator.
	echo Attempting to restart with administrator privileges...
	if defined ARGS (
		 call powershell -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -ArgumentList '%ARGS%' -WorkingDirectory '%SCRIPT_DIR%' -Verb RunAs"
	) else (
		 call powershell -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -WorkingDirectory '%SCRIPT_DIR%' -Verb RunAs"
	)
	exit /b
)
:: Install Chocolatey if not already installed
choco -v >nul 2>&1
if %errorlevel% neq 0 (
	echo Chocolatey is not installed. Installing Chocolatey...
	call powershell -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
)
:: Install Python if not already installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
	echo Python is not installed. Installing Python...
	call choco install python -y
)
:: Install missing packages if any
if not "%PROGRAMS_CHECK%"=="0" (
	call choco install %missing_prog_array% -y --force
	set "PROGRAMS_CHECK=0"
	set "missing_prog_array="
)
:: Install Conda if not already installed
if not "%CONDA_CHECK_STATUS%"=="0" (	
	echo Installing Conda...
	call powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'),'Process')"
	echo Downloading Conda installer...
	call bitsadmin /transfer "MinicondaDownload" %CONDA_URL% "%CONDA_INSTALLER%"
	"%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /AddToPath=1 /S /D=%CONDA_INSTALL_DIR%
	if exist "%CONDA_INSTALL_DIR%\condabin\conda.bat" (
		echo Conda installed successfully.
		set "CONDA_CHECK_STATUS=0"
	)
)
:: Install Docker if not already installed
if not "%DOCKER_CHECK_STATUS%"=="0" (
	echo Docker is not installed. Installing it now...
	call choco install docker-cli docker-engine -y
	call docker --version >nul 2>&1
	if %errorlevel% equ 0 (
		echo Starting Docker Engine...
		net start com.docker.service >nul 2>&1
		if %errorlevel% equ 0 (
			echo Docker installed and started successfully.
			set "DOCKER_CHECK_STATUS=0"
		) 
	)
)
:: Build Docker image if required
if not "%DOCKER_BUILD_STATUS%"=="0" (
	call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
	call python -m pip install -e .
	call docker build -f DockerfileUtils -t utils .
	call conda deactivate
	call docker images -q %DOCKER_UTILS_IMG% >nul 2>&1
	if %errorlevel% equ 0 (
		set "DOCKER_BUILD_STATUS=0"
	)
)
net session >nul 2>&1
if %errorlevel% equ 0 (
    echo Restarting in user mode...
    start "" /b cmd /c "%~f0" %*
    exit /b
)
goto dispatch
exit /b

:dispatch
if "%PROGRAMS_CHECK%"=="0" (
    if "%CONDA_CHECK_STATUS%"=="0" (
        if "%DOCKER_CHECK_STATUS%"=="0" (
			if "%DOCKER_BUILD_STATUS%"=="0" (
				goto main
				exit /b
			)
		) else (
			goto failed
		)
    )
)
goto install_components
exit /b

:main
if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
    python %SCRIPT_DIR%\app.py --script_mode %FULL_DOCKER% %ARGS%
) else (
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		call conda create --prefix %SCRIPT_DIR%\%PYTHON_ENV% python=%PYTHON_VERSION% -y
		call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
		call python -m pip install --upgrade pip
		call python -m pip install beautifulsoup4 coqui-tts ebooklib docker "gradio>=4.44.0" mecab mecab-python3 "nltk>=3.8.2" pydub translate tqdm unidic
		call python -m unidic download
		call python -m spacy download en_core_web_sm
		call python -m nltk.downloader punkt_tab
	) else (
		call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
	)
	python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
	call conda deactivate
)
exit /b

:failed
echo ebook2audiobook is not correctly installed or run.
exit /b

endlocal
pause
