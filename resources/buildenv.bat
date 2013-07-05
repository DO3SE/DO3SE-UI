:: Start a Windows shell (cmd.exe) with the environment variables modified to
:: enable access to all development tools (mSYS, MinGW, G95, Python)
:: assuming they are all in the same directory as this batch script.  This
:: allows a portable bulid environment directory that can be unpacked anywhere.

@echo off

:: Find out where this batch file is
set basepath=%~dp0
:: Modify PATH variable so all tool commands are accessible
set PATH=%basepath%MinGW\msys\1.0\bin;%PATH%
set PATH=%basepath%MinGW\bin;%PATH%
set PATH=%basepath%Python33;%basepath%Python33\Scripts;%PATH%
set PATH=%basepath%;%PATH%
:: Modify LIBRARY_PATH variable so tool libraries can be found
set LIBRARY_PATH=%basepath%MinGW\lib;%PATH%

:: Drop to a normal shell, passing arguments
cmd %*
:: Exit the batch script so the user doesn't get a prompt when exiting the
:: cmd.exe shell
exit /B 0
