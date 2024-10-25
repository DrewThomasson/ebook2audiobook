@echo off
setlocal enabledelayedexpansion

REM Initialize SCRIPT_MODE to empty string
set "SCRIPT_MODE="

set "NATIVE=native"
set "DOCKER_UTILS=docker_utils"
set "FULL_DOCKER=full_docker"

REM Define paths
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "PYTHON_ENV_DOCKER_UTILS=.\python_env"
set "DOCKER_UTILS_NAME=utils"
set "PYTHON_INSTALL_ENV=python_env"

REM List of programs to check
set "REQUIRED_PROGRAMS=calibre ffmpeg"

REM Initialize the return code
set "RETURN_CODE=0"

REM Loop through the list of programs and check if they are installed
for %%p in (%REQUIRED_PROGRAMS%) do (
    where %%p >nul 2>&1
    if errorlevel 1 (
        echo %%p is not installed
        set RETURN_CODE=1
        goto after_check
    )
)

:after_check
REM Check the result of the program check and display appropriate messages
if %RETURN_CODE%==0 (
    echo All required programs are installed.
    REM Set SCRIPT_MODE to NATIVE if all programs are installed
    set SCRIPT_MODE=%NATIVE%
)

REM Function to check if Docker is installed and running
set "RETURN_CODE=0"

REM Check if Docker is installed by checking if 'docker' command is available
where docker >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed.
    set "RETURN_CODE=1"
    goto after_check_docker
) else (
    echo Docker is installed.
)

REM Check if Docker service is running
for /f "tokens=*" %%i in ('docker info 2^>nul') do (
    if not "%%i"=="" (
        echo Docker is running.
        goto after_check_docker
    )
)

REM If no output from docker info, Docker is not running
echo Docker is not running.
set "RETURN_CODE=1"

:after_check_docker
REM Continue the script based on Docker status
if %RETURN_CODE%==0 (
    if exist .\python_env (
        echo Running in docker utils mode
        for /f "delims=" %%i in ('cd') do set "PYTHON_INSTALL_ENV=%%i\python_env"
        set "SCRIPT_MODE=%DOCKER_UTILS%"
    ) else (
		REM Check if the script is running in a Docker container
		if defined container (
			echo Running in full docker mode
			set "SCRIPT_MODE=%FULL_DOCKER%"
		) else (
			set SCRIPT_MODE=%NATIVE%
		)
    )
)

REM Check the script mode and handle accordingly
if "%SCRIPT_MODE%"=="%NATIVE%" (
    python app.py --script_mode "%NATIVE%" %*
) else if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
    set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
    set "PATH=%CONDA_PATH%;%PATH%"
    
    REM Check if Conda is installed
    where conda >nul 2>&1
    if errorlevel 1 (
        echo Conda is not installed. Please install it first.
    ) else (
        REM Check if the Docker image exists
        docker images -q %DOCKER_UTILS_NAME% >nul 2>&1
        if errorlevel 0 (
            REM Activate the Conda environment and run the Python app
            call conda activate %PYTHON_INSTALL_ENV%
            python app.py --script_mode "docker_utils" %*
            call conda deactivate
        ) else (
            echo Docker image '%DOCKER_UTILS_NAME%' not found. Please build or pull the image.
        )
    )
) else if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
    python app.py --script_mode "%FULL_DOCKER%" %*
) else (
    echo ebook2audiobook is not correctly installed. Try running install.bat again.
)

pause  REM Keep the terminal open after the script finishes
