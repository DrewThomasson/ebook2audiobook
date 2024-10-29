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
if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
	echo Running in %DOCKER_UTILS% mode
)
if "%SCRIPT_MODE%"=="%NATIVE%" (
	echo Running in %NATIVE% mode
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
if not "%CURRENT_ENV%"=="" (
	echo Current python virtual environment detected: %CURRENT_ENV%. 
	echo This script runs with its own virtual env and must be out of any other virtual environment when it's launched.
	goto failed
)
goto conda_check

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
goto conda_check

:conda_check
where conda >nul 2>&1
if not %errorlevel%==0 (
	set "CONDA_CHECK_STATUS=1"
	goto install_packages
)
if not "%missing_prog_array%"=="" (
    set "PROGRAMS_CHECK=1"
    goto install_packages
)
if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
	goto docker_check
)
goto backward_privileges

:docker_check
docker --version >nul 2>&1
if %errorlevel% equ 0 (
	:: Verify Docker is running
	docker info >nul 2>&1
	if %errorlevel% equ 0 (
		:: Check if the Docker image is available
		docker images -q %DOCKER_UTILS_IMG% >nul 2>&1
		if %errorlevel% neq 0 (
			echo Docker image '%DOCKER_UTILS_IMG%' not found. Installing it now...
			set "DOCKER_BUILD_STATUS=1"
			goto install_packages
		) else (
			goto backward_privileges
		)
	) else (
		echo Docker is installed but not running. Exiting...
		goto failed
	)
)
set "DOCKER_CHECK_STATUS=1"
goto install_packages

:install_packages
:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
	echo This script needs to be run as administrator.
	echo Attempting to restart with administrator privileges...
	if defined ARGS (
		 powershell -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -ArgumentList '%ARGS%' -WorkingDirectory '%SCRIPT_DIR%' -Verb RunAs"
	) else (
		 powershell -ExecutionPolicy Bypass -Command "Start-Process '%~f0' -WorkingDirectory '%SCRIPT_DIR%' -Verb RunAs"
	)
	exit /b
)
choco -v >nul 2>&1
if %errorlevel% neq 0 (
	echo Chocolatey is not installed. Installing Chocolatey...
	powershell -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
)
python --version >nul 2>&1
if %errorlevel% neq 0 (
	echo Python is not installed. Installing Python...
	choco install python -y
)
if not "%PROGRAMS_CHECK%"=="0" (
	if not "%missing_prog_array%"=="" (
		choco install %missing_prog_array% -y --force
		set "PROGRAMS_CHECK=0"
		set "missing_prog_array="
	)
)
if not "%CONDA_CHECK_STATUS%"=="0" (	
	echo Installing conda...!
	powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'),'Process')"
	echo Downloading conda installer...!
	bitsadmin /transfer "MinicondaDownload" %CONDA_URL% "%CONDA_INSTALLER%"
	"%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /AddToPath=1 /S /D=%CONDA_INSTALL_DIR%
	if exist "%CONDA_INSTALL_DIR%\condabin\conda.bat" (
		echo conda installed successfully.
		set "CONDA_CHECK_STATUS=0"
	)
)
if not "%DOCKER_CHECK_STATUS%"=="0" (
	echo Docker is not installed. Installing it now...
	choco install docker-cli docker-engine -y
	docker --version >nul 2>&1
	if %errorlevel% equ 0 (
		:: Start Docker Engine as a service (only works 
		:: if installed with WSL2 or Linux-based system)
		echo Starting Docker Engine...
		net start com.docker.service >nul 2>&1
		if %errorlevel% equ 0 (
			echo docker installed successfully.
			set "DOCKER_CHECK_STATUS=0"
		) 
	)
)
if not "%DOCKER_BUILD_STATUS%"=="0" (
	call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
	python -m pip install -e .
	docker build -f DockerfileUtils -t utils .
	call conda deactivate
	:: Check if the Docker image is available
	docker images -q %DOCKER_UTILS_IMG% >nul 2>&1
	if %errorlevel% equ 0 (
		set "DOCKER_BUILD_STATUS=0"
	)
)
if "%PROGRAMS_CHECK%"=="0" (
	if "%CONDA_CHECK_STATUS%"=="0" (
		if "%DOCKER_CHECK_STATUS%"=="0" (
			if "%DOCKER_CHECK_STATUS%"=="0" (
				if "%DOCKER_BUILD_STATUS%"=="0" (
					goto backward_privileges
				)
			)
		)
	)
)

:backward_privileges
net session >nul 2>&1
if %errorlevel% equ 0 (
	echo restarting in user mode...
	start "" /b cmd /c "%~f0"
	exit /b
)
goto main

:main
if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
    python %SCRIPT_DIR%\app.py --script_mode %FULL_DOCKER% %ARGS%
) else (
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		call conda create --prefix %SCRIPT_DIR%\%PYTHON_ENV% python=%PYTHON_VERSION% -y
		call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
		python -m pip install --upgrade pip
		python -m pip install pydub beautifulsoup4 ebooklib translate coqui-tts tqdm mecab mecab-python3 docker unidic "nltk>=3.8.2" "gradio>=4.44.0"
		python -m unidic download
		python -m spacy download en_core_web_sm
		python -m nltk.downloader punkt_tab
	) else (
		call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
	)
	python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
	call conda deactivate
)

:failed
echo ebook2audiobook is not correctly installed or run.

endlocal
pause
