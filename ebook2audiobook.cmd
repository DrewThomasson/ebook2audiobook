@echo off

setlocal enabledelayedexpansion

for /f "tokens=2 delims==" %%i in ('"wmic os get Caption /value"') do set OS=%%i
reg query HKCU\Console /v VirtualTerminalLevel >nul 2>&1
if %errorlevel% neq 0 reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul

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
set "PYTHON_ENV=python_env"
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "CURRENT_ENV="
set "PROGRAMS_LIST=calibre-normal ffmpeg nodejs espeak-ng sox tesseract"
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
set "PATH=%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%;%PATH%" 2>&1 >nul
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
	echo ^[[31m=============== Error: 32-bit architecture is not supported.^[[0m
	goto :failed
)

if not exist "%INSTALLED_LOG%" (
	type nul > "%INSTALLED_LOG%"
)

if /i "%arguments_script_mode%"=="%BUILD_DOCKER%" (
    set SCRIPT_MODE=%arguments_script_mode%
)

cd /d "%SCRIPT_DIR%"

goto :check_scoop

:check_scoop
where /Q scoop
if %errorlevel% neq 0 (
	echo Scoop is not installed. 
	set "OK_SCOOP=1"
	goto :install_components
)
goto :check_conda
exit /b

:check_conda
where /Q conda
if %errorlevel% neq 0 (
	echo Miniforge3 is not installed.
	set "OK_CONDA=1"
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
	echo ^[[31m=============== This script runs with its own virtual env and must be out of any other virtual environment when it's launched.^[[0m
	goto :failed
)
goto :check_required_programs
exit /b

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

:check_required_programs
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
	set "OK_PROGRAMS=1"
	goto :install_components
)
goto :dispatch
exit /b

:install_components
if not "%OK_SCOOP%"=="0" (
	echo Installing Scoop...
	call powershell -command "Set-ExecutionPolicy RemoteSigned -scope CurrentUser"
	call powershell -command "iwr -useb get.scoop.sh | iex"
	where /Q scoop
	if !errorlevel! equ 0 (
		echo Scoop installed successfully.
		call scoop install git
		call scoop bucket add muggle https://github.com/hu3rror/scoop-muggle.git
		call scoop bucket add extras
		call scoop bucket add versions
		if "%OK_PROGRAMS%"=="0" (
			echo ^[[32m=============== Scoop is installed! ===============^[[0m
			set "OK_SCOOP=0"
		)
		findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo scoop>>"%INSTALLED_LOG%"
		)
		start "" cmd /k cd /d "%SCRIPT_DIR%" ^& call "%~f0"
	) else (
		echo ^[[31m=============== Scoop installation failed.^[[0m
		goto :failed
	)
	exit
)
if not "%OK_CONDA%"=="0" (
	echo Installing Miniforge...
	call powershell -Command "Invoke-WebRequest -Uri %CONDA_URL% -OutFile "%CONDA_INSTALLER%"
	call start /wait "" "%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniforge3
	where /Q conda
	if !errorlevel! equ 0 (
		echo ^[[32m=============== Miniforge3 is installed! ===============^[[0m
		findstr /i /x "Miniforge3" "%INSTALLED_LOG%" >nul 2>&1
		if errorlevel 1 (
			echo Miniforge3>>"%INSTALLED_LOG%"
		)
	) else (
		echo ^[[31m=============== Miniforge3 installation failed.^[[0m
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
	echo Conda installed successfully.
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
			if !errorlevel! equ 0 (
				for /f %%i in ('call :get_iso3_lang %syslang%') do set "tesslang=%%i"
				echo Detected system language: !syslang! ? downloading OCR language: !tesslang!
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
		) else if "%%p"=="nodejs" (
			set "prog=node"
		) else if "%%p"=="calibre-normal" (
			set "prog=calibre"
		)
		where /Q !prog!
		if !errorlevel! equ 0 (
			echo -e "\e[32m=============== %%p is installed! ===============\e[0m"
			findstr /i /x "%%p" "%INSTALLED_LOG%" >nul 2>&1
			if errorlevel 1 (
				echo %%p>>"%INSTALLED_LOG%"
			)
		) else (
			echo ^[[31m=============== %%p installation failed.^[[0m
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
goto :install_components
exit /b

:main
if "%SCRIPT_MODE%"=="%BUILD_DOCKER%" (
	call python %SCRIPT_DIR%\app.py --script_mode %SCRIPT_MODE% %ARGS%
) else (
	if not exist "%SCRIPT_DIR%\%PYTHON_ENV%" (
		echo Creating ./python_env version %PYTHON_ENV%...
		call "%CONDA_HOME%\Scripts\activate.bat"
		call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
		call conda update --all -y
		call conda clean --index-cache -y
		call conda clean --packages --tarballs -y
		call conda activate base
		call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
		call python3 -m pip cache purge >nul 2>&1
		call python3 -m pip install --upgrade pip
		call python3 -m pip install --upgrade --no-cache-dir --progress-bar ascii --disable-pip-version-check --use-pep517 -r "%SCRIPT_DIR%\requirements.txt"
		for /f "tokens=2 delims= " %%A in ('pip show torch 2^>nul ^| findstr /b /i "Version:"') do set "torch_ver=%%A"
		call python3 -c "import sys;from packaging.version import Version as V;t='!torch_ver!';sys.exit(0 if V(t)<=V('2.2.2') else 1)" >nul 2>&1
		if !errorlevel!==0 (
			call pip install --no-cache-dir --use-pep517 "numpy<2"
		)
		set "src_pyfile=%SCRIPT_DIR%\components\sitecustomize.py"
		for /f "usebackq delims=" %%A in (`python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"`) do set "site_packages_path=%%A"
		set "dst_pyfile=%site_packages_path%\sitecustomize.py"
		if not exist "%dst_pyfile%" (
			call copy /Y "%src_pyfile%" "%dst_pyfile%" >nul
			echo Installed sitecustomize.py hook in %dst_pyfile%
		)
		for %%F in ("%src_pyfile%") do set "src_time=%%~tF"
		if exist "%dst_pyfile%" for %%F in ("%dst_pyfile%") do set "dst_time=%%~tF"
		if "!src_time!" GTR "!dst_time!" (
			call copy /Y "%src_pyfile%" "%dst_pyfile%" >nul
			echo Updated sitecustomize.py hook in %dst_pyfile%
		)
		call python -m unidic download
		if !errorlevel! equ 0 (
			echo ^[[32m=============== unidic dictionary is installed! ===============^[[0m
		) else (
			echo ^[[31m=============== Failed to download unidic dictionary.^[[0m
			goto :failed
		)
		echo All required packages are installed.
	) else (
			call "%CONDA_HOME%\Scripts\activate.bat"
			call conda activate base
			call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"
	)

	call :build_gui
	call python "%SCRIPT_DIR%\app.py" --script_mode %SCRIPT_MODE% %ARGS%
	call conda deactivate
)
exit /b

:failed
echo ^[[31m=============== ebook2audiobook is not correctly installed.^[[0m
exit /b

endlocal
pause