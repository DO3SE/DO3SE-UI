Development Build Environment
=============================

:file:`DO3SE_buildenv_F` -- Minimal Fortran90/F build environment
-----------------------------------------------------------------

1.  Create a :file:`DO3SE_buildenv_F` directory somewhere (the rest of the instructions will assume 
    :file:`C:\\DO3SE_buildenv_F`).
2.  Download the latest stable "Self-extracting Windows x86" installer for the G95_ Fortran 
    compiler.
3.  Run the G95 installer, and install to :file:`C:\\DO3SE_buildenv_F\\g95`.
      * When prompted :guilabel:`Install MinGW utilities and libs?` click :guilabel:`OK`.
      * When prompted :guilabel:`Set PATH = ...` click :guilabel:`Cancel`.
4.  Download the MSYS_ 1.0.11 installer (later versions do not have an installer).
5.  Run the MSYS installer, and install to :file:`C:\\DO3SE_buildenv_F\\msys\\1.0`.
      * Answer :guilabel:`n` to all questions asked by the post-install process.
6.  Copy :file:`resources/buildenv.bat` from the DO3SE source directory to 
    :file:`C:\\DO3SE_buildenv_F`.
7.  Bundle up the :file:`DO3SE_buildenv_F` directory with your tool of choice and distribute it.  I 
    recommend either making a ZIP file, or using 7-zip_ to create a self-extracting (SFX) 7z archive 
    (which creates a much smaller file).


:file:`DO3SE_buildenv_GUI` -- Full GUI build environment
--------------------------------------------------------

These instructions are for building up a directory of tools such they can then be used on another 
machine without downloading or installing anything else or assuming anything else is installed.  
This is particularly useful if somebody wanting to build the GUI doesn't have Administrator 
privileges.  Creating this build environment in the first place, however, will require Administrator 
privileges, since most installers modify the registry.

1.  Follow the instructions for :file:`DO3SE_buildenv_GUI`, but instead using a directory called 
    :file:`DO3SE_buildenv_GUI` (the rest of the instructions assume :file:`C:\\DO3SE_buildenv_GUI`).
2.  Download the latest MinGW_ "Automated installer".  Run it and install to 
    :file:`C:\\DO3SE_buildenv_GUI\\MinGW`.
3.  Download the latest release of Python_ 2.6 (as of writing, there is no NumPy build for 2.7 and 
    the DO3SE GUI is not compatible with Python 3).  Install to 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26`.  **It is essential that you select "Install just for 
    me" otherwise the bundle will not work on another computer.** [#novcredist]_
4.  Download the latest Python 2.6 release of NumPy_.  Run the installer; it should autodetect where 
    to install if you only have one installation of Python on your system, but make sure the one it 
    has detected is in your :file:`DO3SE_buildenv_GUI` directory.
5.  Download the latest :guilabel:`win32-unicode` Python 2.6 release of wxPython_.  Run the 
    installer; it should automatically detect where to install, which will be a path like 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26\\Lib\\site-packages`.  If it is incorrect, change the 
    part before :file:`Python26` to be your :file:`DO3SE_buildenv_GUI` directory.
6.  Download the latest version of py2exe_ which ends in :file:`.win32-py2.6.exe`.  Run the 
    installer; the process should be identical to that for NumPy.
    
      * If the installer fails to run, you may need to install the "Microsoft Visual C++ 2008 
        Redistributable" which can be `downloaded here 
        <http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en>`_.

7.  Download the `7-Zip Command Line Version`_ and unzip it somewhere.  Copy the :file:`7za.exe` 
    into your :file:`DO3SE_buildenv_GUI` directory.
8.  If you have not already done so, copy :file:`resources/buildenv.bat` from the DO3SE source 
    directory to :file:`C:\\DO3SE_buildenv_GUI`.
9.  Copy the :file:`resources/Microsoft.VC90.CRT` directory from the DO3SE source directory to 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26\\Lib\\site-packages\\wx-2.8-msw-unicode\wx` and to 
    :file:`site-packages\\py2exe`.  [#novcredist]_
10. Bundle up the :file:`DO3SE_buildenv_GUI` directory in the same way as :file:`DO3SE_buildenv_F`.


.. [#novcredist] Necessary to remove dependency on having Visual C++ redistributable installed.


.. _G95: http://www.g95.org/downloads.shtml
.. _MSYS: http://sourceforge.net/downloads/mingw/MSYS/BaseSystem/
.. _MinGW: http://sourceforge.net/downloads/mingw/Automated%20MinGW%20Installer/
.. _Python: http://python.org/download/releases/
.. _NumPy: http://sourceforge.net/projects/numpy/files/NumPy/
.. _wxPython: http://www.wxpython.org/download.php#binaries
.. _py2exe: http://sourceforge.net/projects/py2exe/files/
.. _7-zip: http://www.7-zip.org/
.. _7-Zip Command Line Version: http://www.7-zip.org/download.html
