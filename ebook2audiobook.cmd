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
set "PROGRAMS_LIST=calibre-normal-cjk ffmpeg nodejs espeak-ng curl"

set "TMP=%SCRIPT_DIR%\tmp"
set "TEMP=%SCRIPT_DIR%\tmp"
set "ESPEAK_DATA_PATH=%USERPROFILE%\scoop\apps\espeak-ng\current\eSpeak NG\espeak-ng-data"
set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "SCOOP_HOME=%USERPROFILE%\scoop"
set "SCOOP_SHIMS=%SCOOP_HOME%\shims"
set "SCOOP_APPS=%SCOOP_HOME%\apps"
set "SCOOP_BUCKETS=muggle extras versions"
set "CONDA_URL=https://repo.anaconda.com/miniconda/Miniconda3-py312_24.1.2-0-Windows-x86_64.exe"
set "CONDA_INSTALLER=%TEMP%\miniconda.exe"
set "CONDA_INSTALL_DIR=%USERPROFILE%\miniconda3"
set "CONDA_BAT=%CONDA_INSTALL_DIR%\condabin\conda.bat"
set "CONDA_PATH=%USERPROFILE%\miniconda3\bin"
set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%CONDA_INSTALL_DIR%;%CONDA_INSTALL_DIR%\Scripts;%PATH%"

set "SCOOP_CHECK_STATUS=0"
set "CONDA_CHECK_STATUS=0"
set "PROGRAMS_CHECK=0"
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
goto scoop_check

:scoop_check
where /Q scoop
if %errorlevel% neq 0 (
	set "SCOOP_CHECK_STATUS=1"
)
goto conda_check
exit /b

:conda_check
where /Q conda
if %errorlevel% neq 0 (
	call rmdir /s /q "%CONDA_INSTALL_DIR%" 2>nul
	set "CONDA_CHECK_STATUS=1"
	goto programs_check
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
	goto failed
)
goto programs_check
exit /b

:programs_check
set "missing_prog_array="
for %%p in (%PROGRAMS_LIST%) do (
    set "prog=%%p"
    if "%%p"=="nodejs" set "prog=node"
	if "%%p"=="calibre-normal-cjk" set "prog=calibre"
    where /Q !prog!
    if !errorlevel! neq 0 (
        echo %%p is not installed.
        set "missing_prog_array=!missing_prog_array! %%p"
    )
)
if not "!missing_prog_array!"=="" (
    set "PROGRAMS_CHECK=1"
    goto install_components
)
goto dispatch
exit /b

:install_components
:: Install Scoop if not already installed
if not "%SCOOP_CHECK_STATUS%"=="0" (
	echo Scoop is not installed. Installing Scoop...
	powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -useb get.scoop.sh | iex"
	timeout /t 6 /nobreak >nul
	where /Q scoop
	if !errorlevel! neq 0 (
		echo Scoop installation failed.
		goto failed
	)
	scoop install git
	set "installed_buckets="
	for /f "tokens=1" %%b in ('scoop bucket list ^| findstr /V "Name ----"') do (
		set "installed_buckets=!installed_buckets! %%b"
	)
	for %%b in (%SCOOP_BUCKETS%) do (
		set "found=0"
		for %%i in (!installed_buckets!) do (
			if "%%i"=="%%b" set "found=1"
		)
		if !found!==0 (
			echo Adding missing bucket: %%b...
			if /i "%%b"=="muggle" (
				scoop bucket add %%b https://github.com/hu3rror/scoop-muggle.git
			) else (
				scoop bucket add %%b
			)
			set "installed_buckets=!installed_buckets! %%b"
		) else (
			echo Bucket %%b is already registered.
		)
	)
	echo Scoop installed successfully.
	set "SCOOP_CHECK_STATUS=0"
)
:: Install missing packages one by one
if not "%PROGRAMS_CHECK%"=="0" (
    echo Installing missing programs...
    for %%p in (%missing_prog_array%) do (
		echo Installing %%p...
		scoop install %%p
    )
    set "PROGRAMS_CHECK=0"
    set "missing_prog_array="
)
:: Install Conda if not already installed
if not "%CONDA_CHECK_STATUS%"=="0" (
	echo Installing Miniconda3...
	curl "%CONDA_URL%" -o "%CONDA_INSTALLER%"
	start /wait "" "%CONDA_INSTALLER%" /S
	where /Q conda
	if !errorlevel! neq 0 (
		echo Conda installation failed.
		goto failed
	)
	call conda update conda -y
	del %CONDA_INSTALLER%
	set "CONDA_CHECK_STATUS=0"
	echo Conda installed successfully.
)
goto dispatch
exit /b

:dispatch
if "%SCOOP_CHECK_STATUS%"=="0" (
	if "%PROGRAMS_CHECK%"=="0" (
		if "%CONDA_CHECK_STATUS%"=="0" (
			if "%DOCKER_CHECK_STATUS%"=="0" (
				goto main
			) else (
				goto failed
			)
		)
	)
)
echo PROGRAMS_CHECK: %PROGRAMS_CHECK%
echo CONDA_CHECK_STATUS: %CONDA_CHECK_STATUS%
echo DOCKER_CHECK_STATUS: %DOCKER_CHECK_STATUS%
goto install_components
exit /b

:main
if "%SCRIPT_MODE%"=="%FULL_DOCKER%" (
	call python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
) else (
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
		call %CONDA_BAT% activate base
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
		call python -m pip cache purge
		call python -m pip install --upgrade pip
		for /f %%p in (requirements.txt) do (
			echo Installing %%p...
			python -m pip install --upgrade --no-cache-dir --progress-bar=on %%p
		)
		echo All required packages are installed.
	) else (
		call %CONDA_BAT% activate base
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
	)
	call python "%SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
)
exit /b

:failed
echo ebook2audiobook is not correctly installed or run.
exit /b

endlocal
pause