@echo off
setlocal enabledelayedexpansion

:: Capture all arguments into ARGS
set "ARGS=%*"
set "NATIVE=native"
set "FULL_DOCKER=full_docker"
set "SCRIPT_MODE=%NATIVE%"
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "APP_NAME=ebook2audiobook"
set /p APP_VERSION=<"%SCRIPT_DIR%\VERSION.txt"
set "APP_FILE=%APP_NAME%.cmd"
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

set "SCOOP_CHECK=0"
set "CONDA_CHECK=0"
set "PROGRAMS_CHECK=0"
set "DOCKER_CHECK=0"

:: Refresh environment variables (append registry Path to current PATH)
for /f "tokens=2,*" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path') do (
    set "PATH=%%B;%PATH%"
)

cd /d "%SCRIPT_DIR%"

if "%ARCH%"=="x86" (
    echo Error: 32-bit architecture is not supported.
    goto :failed
)

if not exist "%INSTALLED_LOG%" (
	type nul > "%INSTALLED_LOG%"
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
if not "%SCOOP_CHECK%"=="0" (
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
        if "%PROGRAMS_CHECK%"=="0" (
            set "SCOOP_CHECK=0"
        )
        findstr /i /x "scoop" "%INSTALLED_LOG%" >nul 2>&1
        if errorlevel 1 (
            echo scoop>>"%INSTALLED_LOG%"
        )
        start "" cmd /k cd /d "%SCRIPT_DIR%" ^& call "%~f0"
    ) else (
        echo Conda installation failed.
        goto :failed
    )
    exit
)
if not "%CONDA_CHECK%"=="0" (
    echo Installing Miniforge...
    call powershell -Command "Invoke-WebRequest -Uri %CONDA_URL% -OutFile "%CONDA_INSTALLER%"
    call start /wait "" "%CONDA_INSTALLER%" /InstallationType=JustMe /RegisterPython=0 /S /D=%UserProfile%\Miniforge3
    where /Q conda
    if !errorlevel! equ 0 (
        findstr /i /x "Miniforge3" "%INSTALLED_LOG%" >nul 2>&1
        if errorlevel 1 (
            echo Miniforge3>>"%INSTALLED_LOG%"
        )
    ) else (
        echo Conda installation failed.
        goto :failed
    )
    if not exist "%USERPROFILE%\.condarc" (
        call conda config --set auto_activate false
    )
    call conda update conda -y
    del "%CONDA_INSTALLER%"
    set "CONDA_CHECK=0"
    echo Conda installed successfully.
    start "" cmd /k cd /d "%CD%" ^& call "%~f0"
    exit
)
if not "%PROGRAMS_CHECK%"=="0" (
    echo Installing missing programs...
    if "%SCOOP_CHECK%"=="0" (
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
                set "syslang=%LANG%"
                if not defined syslang set "syslang=en"
                set "syslang=!syslang:~0,2!"
                set "tesslang=eng"
                if /I "!syslang!"=="fr" set "tesslang=fra"
                if /I "!syslang!"=="de" set "tesslang=deu"
                if /I "!syslang!"=="it" set "tesslang=ita"
                if /I "!syslang!"=="es" set "tesslang=spa"
                if /I "!syslang!"=="pt" set "tesslang=por"
                if /I "!syslang!"=="ar" set "tesslang=ara"
                if /I "!syslang!"=="tr" set "tesslang=tur"
                if /I "!syslang!"=="ru" set "tesslang=rus"
                if /I "!syslang!"=="bn" set "tesslang=ben"
                if /I "!syslang!"=="zh" set "tesslang=chi_sim"
                if /I "!syslang!"=="fa" set "tesslang=fas"
                if /I "!syslang!"=="hi" set "tesslang=hin"
                if /I "!syslang!"=="hu" set "tesslang=hun"
                if /I "!syslang!"=="id" set "tesslang=ind"
                if /I "!syslang!"=="jv" set "tesslang=jav"
                if /I "!syslang!"=="ja" set "tesslang=jpn"
                if /I "!syslang!"=="ko" set "tesslang=kor"
                if /I "!syslang!"=="pl" set "tesslang=pol"
                if /I "!syslang!"=="ta" set "tesslang=tam"
                if /I "!syslang!"=="te" set "tesslang=tel"
                if /I "!syslang!"=="yo" set "tesslang=yor"
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
            findstr /i /x "%%p" "%INSTALLED_LOG%" >nul 2>&1
            if errorlevel 1 (
                echo %%p>>"%INSTALLED_LOG%"
            )
        ) else (
            echo %%p installation failed...
            goto :failed
        )
    )
    call powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%SCOOP_SHIMS%;%SCOOP_APPS%;%CONDA_PATH%;%NODE_PATH%', 'User')"
    set "SCOOP_CHECK=0"
    set "PROGRAMS_CHECK=0"
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
			echo Creating ./python_env version %PYTHON_ENV%...
			call "%CONDA_HOME%\Scripts\activate.bat"
			call conda create --prefix "%SCRIPT_DIR%\%PYTHON_ENV%" python=%PYTHON_VERSION% -y
			call conda activate base
			call conda activate "%SCRIPT_DIR%\%PYTHON_ENV%"

			call python -m pip cache purge >nul 2>&1
			call python -m pip install --upgrade pip

			for /f "usebackq delims=" %%p in ("requirements.txt") do (
				echo Installing %%p...
				call python -m pip install --upgrade --no-cache-dir --use-pep517 --progress-bar=on "%%p"
			)

			set "components_dir=C:\path\to\components"
			set "src_pyfile=%components_dir%\sitecustomize.py"
			set "dst_pyfile=%site_packages_path%\sitecustomize.py"

			for /f "usebackq delims=" %%A in (`python -c "import sysconfig; print(sysconfig.get_paths()['purelib'])"`) do (
				set "site_packages_path=%%A"
			)

			if not exist "%dst_pyfile%" (
				copy /Y "%src_pyfile%" "%dst_pyfile%"
				echo Installed sitecustomize.py hook → %dst_pyfile%
			)

			for %%F in ("%src_pyfile%") do set "src_time=%%~tF"
			for %%F in ("%dst_pyfile%") do set "dst_time=%%~tF"

			:: If source is newer
			if "!src_time!" GTR "!dst_time!" (
				copy /Y "%src_pyfile%" "%dst_pyfile%"
				echo Updated sitecustomize.py hook → %dst_pyfile%
			)
			
			for /f "tokens=2 delims= " %%A in ('pip show torch 2^>nul ^| findstr /b /i "Version:"') do (
				set "torch_ver=%%A"
			)

			echo Detected torch version: %torch_ver%

			python -c "import sys;from packaging.version import Version as V;t='%torch_ver%';sys.exit(0 if V(t)<=V('2.2.2') else 1)" >nul 2>&1

			if %errorlevel%==0 (
				echo torch version requires numpy^<2. Installing numpy 1.26.4...
				pip install --no-cache-dir --use-pep517 "numpy<2"
			) else (
				echo torch version is fine. No numpy downgrade needed.
			)

			python -m unidic download
			if %errorlevel% neq 0 (
				echo Failed to download unidic.
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
echo ebook2audiobook is not correctly installed or run.
exit /b

endlocal
pause