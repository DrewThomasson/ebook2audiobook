@echo off
setlocal enabledelayedexpansion

REM Initialize SCRIPT_MODE to empty string
set "SCRIPT_MODE="

set "NATIVE=native"
set "DOCKER_UTILS=docker_utils"
set "FULL_DOCKER=full_docker"

set "DOCKER_IMG=utils"

REM Define paths
set "MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "MINICONDA_INSTALLER=%TEMP%\Miniconda3-latest-Windows-x86_64.exe"
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "INSTALL_DIR=%USERPROFILE%\miniconda3"
set "CONDA_STATUS=0"
set "PATH=%CONDA_PATH%;%PATH%"
set "PYTHON_ENV_NATIVE=native_env"
set "PYTHON_ENV_DOCKER_UTILS=python_env"

REM List of programs to check
set "REQUIRED_PROGRAMS=calibre ffmpeg"

set "PROGRAMS_STATUS=0"
for %%p in (%REQUIRED_PROGRAMS%) do (
    where %%p >nul 2>&1
    if errorlevel 1 (
		echo  %%p is not installed. Install %%p manually or with install.bat with Administrator level.
        set PROGRAMS_STATUS=1
        goto check_external_programs
    )
)
:check_external_programs
if %PROGRAMS_STATUS%==0 (
    REM Set SCRIPT_MODE to NATIVE if all programs are installed
    set SCRIPT_MODE=%NATIVE%
) else (
    echo Use install.bat as Administrator to install everything needed.!
)

REM Function to check if Docker is installed and running
set "DOCKER_STATUS=0"
where docker >nul 2>&1
if errorlevel 1 (
	echo  %%p Docker is not installed. Install %%p manually or with install.bat with Administrator level.
    set "DOCKER_STATUS=1"
    goto check_docker
)
if %DOCKER_STATUS%==0 (
	REM Check if Docker service is running
	for /f "tokens=*" %%i in ('docker info 2^>nul') do (
		if "%%i"=="" (
			echo  %%p Docker is not running
			set "DOCKER_STATUS=1"
			goto check_docker
		)
	)
) else (
	echo  %%p Use install.bat to install everything needed.
)
:check_docker
if %DOCKER_STATUS%==0 (
    if exist %PYTHON_ENV_DOCKER_UTILS% (
		echo  %%p Running in docker utils mode
        for /f "delims=" %%i in ('cd') do set "PYTHON_ENV_DOCKER_UTILS=%%i\python_env"
        set "SCRIPT_MODE=%DOCKER_UTILS%"
    ) else (
		if defined container (
			echo  %%p Running in full docker mode
			set "SCRIPT_MODE=%FULL_DOCKER%"
		) else (
			set SCRIPT_MODE=%NATIVE%
		)
    )
)

where conda >nul 2>&1
if errorlevel 1 (
    echo Miniconda is not installed!
    set "CONDA_STATUS=1"
    goto check_conda
)
:check_conda
if %CONDA_STATUS%==1 (
    if not "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
        echo Downloading Miniconda installer...!
        bitsadmin /transfer "MinicondaDownload" %MINICONDA_URL% "%MINICONDA_INSTALLER%"

        echo Installing Miniconda...!
        "%MINICONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /AddToPath=1 /S /D=%INSTALL_DIR%

        REM Verify installation by checking if conda.bat exists
        if exist "%INSTALL_DIR%\condabin\conda.bat" (
            echo Miniconda installed successfully.!
            set "CONDA_STATUS=0"
        ) else (
            echo !ESC![31mMiniconda installation failed.!
        )
    )
)

REM Check the script mode and handle accordingly
set "PATH=%INSTALL_DIR%\condabin;%PATH%"
if "%SCRIPT_MODE%"=="%NATIVE%" (
	if %CONDA_STATUS%==0 (
		call conda create --name %PYTHON_ENV_NATIVE% python=3.11 -y
		call conda activate %PYTHON_ENV_NATIVE%
		python app.py --script_mode "%NATIVE%" %*
		call conda deactivate
	)
) else if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
	REM Check if the Docker image exists
	docker images -q %DOCKER_IMG% >nul 2>&1
	if errorlevel 0 (
		call conda create --prefix .\%PYTHON_ENV_DOCKER_UTILS% python=3.11 -y
		call conda activate .\%PYTHON_ENV_DOCKER_UTILS%
		python app.py --script_mode "docker_utils" %*
		call conda deactivate
	) else (
		echo Docker image '%DOCKER_IMG%' not found. Please build or pull the image.
	)
) else if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
    python app.py --script_mode "%FULL_DOCKER%" %*
) else (
	echo  %%p ebook2audiobook is not correctly installed. Try running the installation from install.bat
)

pause
