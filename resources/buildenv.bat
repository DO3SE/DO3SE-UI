:: Start a Windows shell (cmd.exe) with the environment variables modified to
:: enable access to all development tools (mSYS, MinGW, G95, Python)
:: assuming they are all in the same directory as this batch script.  This
:: allows a portable bulid environment directory that can be unpacked anywhere.

@echo off

:: Find out where this batch file is
set basepath=%~dp0
:: Modify PATH variable so all tool commands are accessible
set PATH=%basepath%msys\1.0\bin;%PATH%
set PATH=%basepath%MinGW\bin;%PATH%
set PATH=%basepath%g95\lib\gcc-lib\i686-pc-mingw32\4.0.4;%PATH%
set PATH=%basepath%g95\bin;%PATH%
set PATH=%basepath%Python26;%basepath%Python26\Scripts;%PATH%
set PATH=%basepath%;%PATH%
:: Modify LIBRARY_PATH variable so tool libraries can be found
set LIBRARY_PATH=%basepath%g95\lib\gcc-lib\i686-pc-mingw32\4.0.4;%PATH%
set LIBRARY_PATH=%basepath%g95\lib;%basepath%MinGW\lib;%LIBRARY_PATH%

:: Create an alias for F
doskey F=g95 -std=F $*

:: Drop to a normal shell in the normal location
cd %USERPROFILE%
cmd
:: Exit the batch script so the user doesn't get a prompt when exiting the
:: cmd.exe shell
exit /B 0
