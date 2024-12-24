@echo off
setlocal enabledelayedexpansion

:: Set the path to FFmpeg
set FFmpegPath="C:\path\to\ffmpeg.exe"

:: Root directory to start the search
set RootDir=.

:: Step 1: Find and delete _22khz.wav files
for /r "%RootDir%" %%F in (*_22khz.wav) do (
    echo Deleting "%%F"
    del "%%F"
)

:: Step 2: Find _24khz.wav files and convert them to _16khz.wav
for /r "%RootDir%" %%F in (*_24khz.wav) do (
    set "InputFile=%%F"
    set "OutputFile=%%~dpF%%~nF"
    set "OutputFile=!OutputFile:_24khz=_16khz!.wav"

    echo Converting "!InputFile!" to "!OutputFile!"
    %FFmpegPath% -i "!InputFile!" -ar 16000 "!OutputFile!"
)

echo Done!
pause
