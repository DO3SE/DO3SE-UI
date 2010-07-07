:: Start a Windows shell (cmd.exe) with the environment variables modified to
:: enable access to MinGW, mSYS and G95

@echo off

set basepath=%~dp0
set PATH=%basepath%;%PATH%
set PATH=%basepath%g95\bin;%PATH%
set PATH=%basepath%msys\1.0\bin;%PATH%

set LIBRARY_PATH=%basepath%g95\lib;%LIBRARY_PATH%

:: Drop to a normal shell in the normal location
cd %USERPROFILE%
cmd
:: Exit the batch script so the user doesn't get a prompt when exiting the
:: cmd.exe shell
exit /B 0
