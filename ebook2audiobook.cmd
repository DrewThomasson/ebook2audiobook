@echo off
setlocal enabledelayedexpansion

:: Capture all arguments into ARGS
set "ARGS=%*"

set "NATIVE=native"
set "FULL_DOCKER=full_docker"

set "SCRIPT_MODE=%NATIVE%"
set "SCRIPT_DIR=%~dp0"

set "ARCH=%PROCESSOR_ARCHITECTURE%"
set "PYTHON_VERSION=3.12"
set "PYTHON_ENV=python_env"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="

set "PROGRAMS_LIST=calibre-normal ffmpeg nodejs espeak-ng sox"

set "TMP=%SCRIPT_DIR%\tmp"
set "TEMP=%SCRIPT_DIR%\tmp"

set "ESPEAK_DATA_PATH=%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data"

set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"

set "CONDA_URL=https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
set "CONDA_INSTALL_DIR=%USERPROFILE%\Miniforge3"
set "CONDA_INSTALLER=Miniforge3-Windows-x86_64.exe"
set "CONDA_ENV=%CONDA_INSTALL_DIR%\condabin\conda.bat"
set "CONDA_PATH=%CONDA_INSTALL_DIR%\condabin"

set "NODE_PATH=%SCOOP_HOME%\apps\nodejs\current"

set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%;%PATH%" 2>&1 >nul

set "SCOOP_CHECK=0"
set "CONDA_CHECK=0"
set "PROGRAMS_CHECK=0"
set "DOCKER_CHECK=0"

set "HELP_FOUND=%ARGS:--help=%"

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "PATH=%%B;%PATH%"
)

cd /d "%SCRIPT_DIR%"

if "%ARCH%"=="x86" (
	echo Error: 32-bit architecture is not supported.
	goto :failed
)

:: Check if running inside Docker
if defined CONTAINER (
	set "SCRIPT_MODE=%FULL_DOCKER%"
	goto :main
)

goto :scoop_check

:scoop_check
where /Q scoop
if %errorlevel% neq 0 (
	echo Scoop is not installed. 
	set "SCOOP_CHECK=1"
	goto :install_components
)
goto :conda_check
exit /b

:conda_check
where /Q conda
if %errorlevel% neq 0 (
	call rmdir /s /q "%CONDA_INSTALL_DIR%" 2>nul
	echo Miniforge3 is not installed. 
	set "CONDA_CHECK=1"
	goto :install_components
)
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
	goto :failed
)
goto :programs_check
exit /b

:programs_check
set "missing_prog_array="
for %%p in (%PROGRAMS_LIST%) do (
    set "prog=%%p"
    if "%%p"=="nodejs" set "prog=node"
	if "%%p"=="calibre-normal" set "prog=calibre"
    where /Q !prog!
    if !errorlevel! neq 0 (
        echo %%p is not installed.
        set "missing_prog_array=!missing_prog_array! %%p"
    )
)
if not "%missing_prog_array%"=="" (
    set "PROGRAMS_CHECK=1"
    goto :install_components
)
goto :dispatch
exit /b

:install_components
:: Install Scoop if not already installed
if not "%SCOOP_CHECK%"=="0" (
	echo Installing Scoop...
    call powershell -command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser"
    call powershell -command "iwr -useb get.scoop.sh | iex"
	call scoop install git
	call scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git
	call scoop bucket add extras
	call scoop bucket add versions
	echo Scoop installed successfully.
	if "%PROGRAMS_CHECK%"=="0" (
		set "SCOOP_CHECK=0"
	)
	start "" cmd /k cd /d "%CD%" ^& call "%~f0"
	exit
)
:: Install Conda if not already installed
if not "%CONDA_CHECK%"=="0" (
	echo Installing Miniforge...
	call powershell -Command "Invoke-WebRequest -Uri %CONDA_URL% -OutFile "%CONDA_INSTALLER%"
	call start /wait "" "%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniforge3
	where /Q conda
	if !errorlevel! neq 0 (
		echo Conda installation failed.
		goto :failed
	)
	call conda config --set auto_activate_base false
	call conda update conda -y
	del "%CONDA_INSTALLER%"
	set "CONDA_CHECK=0"
	echo Conda installed successfully.
	start "" cmd /k cd /d "%CD%" ^& call "%~f0"
	exit
)
:: Install missing packages one by one
if not "%PROGRAMS_CHECK%"=="0" (
    echo Installing missing programs...
	if "%SCOOP_CHECK%"=="0" (
		call scoop bucket add muggle b https://github.com/hu3rror/scoop-muggle.git
		call scoop bucket add extras
		call scoop bucket add versions
	)
    for %%p in (%missing_prog_array%) do (
		call scoop install %%p
		set "prog=%%p"
		if "%%p"=="nodejs" (
			set "prog=node"
		)
		if "%%p"=="calibre-normal" set "prog=calibre"
		where /Q !prog!
		if !errorlevel! neq 0 (
			echo %%p installation failed...
			goto :failed
		)
    )
	call powershell -command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + '%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%;', 'User')"
	set "SCOOP_CHECK=0"
    set "PROGRAMS_CHECK=0"
    set "missing_prog_array="
)
goto :dispatch
exit /b

:dispatch
if "%SCOOP_CHECK%"=="0" (
	if "%PROGRAMS_CHECK%"=="0" (
		if "%CONDA_CHECK%"=="0" (
			if "%DOCKER_CHECK%"=="0" (
				goto :main
			) else (
				goto :failed
			)
		)
	)
)
echo PROGRAMS_CHECK: %PROGRAMS_CHECK%
echo CONDA_CHECK: %CONDA_CHECK%
echo DOCKER_CHECK: %DOCKER_CHECK%
goto :install_components
exit /b

:main
if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
	call python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
) else (
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
		call %CONDA_ENV% activate base
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
		call python -m pip cache purge >nul 2>&1
		call python -m pip install --upgrade pip
		for /f "usebackq delims=" %%p in ("requirements.txt") do (
			echo Installing %%p...
			call python -m pip install --upgrade --no-cache-dir --use-pep517 --progress-bar=on "%%p"
		)
		echo All required packages are installed.
	) else (
		call %CONDA_ENV% activate base
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