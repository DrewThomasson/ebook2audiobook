@echo off

REM Parameters passed to the script
set "PARAMS=%*"

REM Check for conda and docker installation
for /f "tokens=2 delims==" %%i in ('conda --version 2^>nul') do set "CONDA_VERSION=%%i"
for /f %%i in ('where docker 2^>nul') do set "DOCKER=%%i"
set "DOCKER_IMG=utils"

REM Activate conda only if conda is installed and the environment exists
if not "%CONDA_VERSION%"=="" if exist ".\python_env" (
    REM Check if Docker image exists
    for /f %%i in ('docker images -q %DOCKER_IMG% 2^>nul') do set "IMG_ID=%%i"
    if not "%IMG_ID%"=="" (
        REM Activate conda environment and run the application
        call conda activate .\python_env

        REM Run the Python application with passed parameters
        python app.py %*

        REM Deactivate conda environment
        call conda deactivate
        timeout /t 1 /nobreak >nul
        call conda deactivate
        goto end
    ) else (
        echo Docker image '%DOCKER_IMG%' not found.
        goto end
    )
) else (
    echo Conda is not installed or virtual python environment is missing.
    goto end
)

:end
REM If we reach here, something went wrong or the script finished
echo ebook2audiobookXTTS is not correctly installed. Try to run install.bat again.
timeout /t 1 /nobreak >nul
call conda deactivate
pause
