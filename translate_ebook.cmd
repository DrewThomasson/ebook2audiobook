@echo off
rem Runs tools\translate_ebook.py with e2a's python_env, every argument forwarded (--help lists the options).
rem Paths are taken from the folder it is started from.
setlocal
set "PY_CMD=%~dp0python_env\Scripts\python.exe"
if exist "%PY_CMD%" goto :run
echo python_env not found: run ebook2audiobook.cmd once to install ebook2audiobook. 1>&2
exit /b 1
:run
rem calibre comes from scoop, as for ebook2audiobook.cmd
set "PATH=%USERPROFILE%\scoop\shims;%PATH%"
"%PY_CMD%" "%~dp0tools\translate_ebook.py" %*
exit /b %ERRORLEVEL%
