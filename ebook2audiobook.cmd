@echo off
setlocal enabledelayedexpansion

:: Capture all arguments into ARGS
set "ARGS=%*"
set "SCRIPT_MODE="

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script needs to be run as administrator.
    echo Attempting to restart with administrator privileges...
    set "ARG_LIST="
    for %%A in (%ARGS%) do (
        set "ARG_LIST=!ARG_LIST!,'%%A'"
    )
    if defined ARG_LIST (
        powershell -Command "Start-Process cmd -ArgumentList '/c', 'cd /d ""%SCRIPT_DIR%""', '&&', '""%~f0""' %ARG_LIST% -Verb RunAs"
    ) else (
        powershell -Command "Start-Process cmd -ArgumentList '/c', 'cd /d ""%SCRIPT_DIR%""', '&&', '""%~f0""' -Verb RunAs"
    )
    exit /b
)

set "PYTHON_VERSION=3.11"
set "NATIVE=native"
set "DOCKER_UTILS=docker_utils"
set "FULL_DOCKER=full_docker"
set "DOCKER_UTILS_IMG=utils"
set "PYTHON_ENV=python_env"
set "REQUIRED_PROGRAMS=calibre ffmpeg"

set "MINICONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe"
set "MINICONDA_INSTALLER=%TEMP%\Miniconda3-latest-Windows-x86_64.exe"
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "INSTALL_DIR=%USERPROFILE%\miniconda3"
set "PATH=%CONDA_PATH%;%PATH%"

:: Check if running inside Docker
if "%SCRIPT_MODE%"=="" (
	if defined CONTAINER (
		set "SCRIPT_MODE=%FULL_DOCKER%"
		goto main
	)
	set "SCRIPT_MODE=%NATIVE%"
) else if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
	goto docker_check
)

set "MISSING_PROGRAMS="
for %%p in (%REQUIRED_PROGRAMS%) do (
    set "FOUND="
    for /f "delims=" %%i in ('where %%p 2^>nul') do (
        set "FOUND=%%i"
    )
    if not defined FOUND (
        echo %%p is not installed.
        set "MISSING_PROGRAMS=!MISSING_PROGRAMS! %%p"
    )
)

if "%MISSING_PROGRAMS%"=="" (
	goto conda_check
) else (
    set "CHOCO_INSTALLED="
    for /f "delims=" %%i in ('where choco 2^>nul') do (
        set "CHOCO_INSTALLED=%%i"
    )
    if not defined CHOCO_INSTALLED (
        echo Installing Chocolatey...
        powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"
    )
    choco install %MISSING_PROGRAMS% -y --force
	goto conda_check
)

:docker_check
set "FOUND="
for /f "delims=" %%i in ('where docker 2^>nul') do (
	set "FOUND=%%i"
)
if not defined FOUND (
	echo Docker is not installed. Installing Docker...
	choco install docker -y
)

:: Verify Docker is running
for /f "tokens=*" %%i in ('docker info 2^>nul') do (
	if "%%i"=="" (
		echo Docker is installed but not running. Exiting...
		goto failed
	)
)

:conda_check
set "CONDA_STATUS=1"
where conda >nul 2>&1
if %errorlevel%==0 (
    set "CONDA_STATUS=0"
)
if defined CONDA_EXE (
    set "CONDA_STATUS=0"
)
if defined CONDA_DEFAULT_ENV (
    set "CONDA_STATUS=0"
)
if %CONDA_STATUS%==0 (
	goto main
) else (
	echo Installing python...
	choco install python -y
	powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [System.Environment]::GetEnvironmentVariable('Path','User'),'Process')"
	echo Downloading Miniconda installer...!
	bitsadmin /transfer "MinicondaDownload" %MINICONDA_URL% "%MINICONDA_INSTALLER%"
	echo Installing Miniconda...!
	"%MINICONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /AddToPath=1 /S /D=%INSTALL_DIR%
	if exist "%INSTALL_DIR%\condabin\conda.bat" (
		echo Miniconda installed successfully.
		goto main
	) else (
		echo Miniconda installation failed.
		goto failed
	)
)

:main
if "%SCRIPT_MODE%"=="%NATIVE%" (
	echo Running in %NATIVE% mode
	if defined VIRTUAL_ENV (
		python app.py --script_mode %NATIVE% %ARGS%
	) else if defined CONDA_DEFAULT_ENV (
		python app.py --script_mode %NATIVE% %ARGS%
	) else (
		if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
			conda create --prefix %SCRIPT_DIR%\%PYTHON_ENV% python=%PYTHON_VERSION% -y
		)
		call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
		python app.py --script_mode %NATIVE% %ARGS%
		call conda deactivate
	)
) else if "%SCRIPT_MODE%"=="%DOCKER_UTILS%" (
    docker images -q %DOCKER_UTILS_IMG% >nul 2>&1
    if errorlevel 0 (
        echo Running in %DOCKER_UTILS% mode
        if defined VIRTUAL_ENV (
            python app.py --script_mode %DOCKER_UTILS% %ARGS%
        ) else if defined CONDA_DEFAULT_ENV (
            python app.py --script_mode %DOCKER_UTILS% %ARGS%
        ) else (
            if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
                conda create --prefix %SCRIPT_DIR%\%PYTHON_ENV% python=%PYTHON_VERSION% -y
            )
            call conda activate %SCRIPT_DIR%\%PYTHON_ENV%
            python app.py --script_mode %DOCKER_UTILS% %ARGS%
            call conda deactivate
        )
    ) else (
        echo Docker image '%DOCKER_UTILS_IMG%' not found. build it now...
    )
) else if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
    echo Running in %FULL_DOCKER% mode
    python app.py --script_mode %FULL_DOCKER% %ARGS%
) else (
    echo ebook2audiobook is not correctly installed. Run the installation script to set it up.
)

:failed
echo ebook2audiobook is not correctly installed.

endlocal
pause
