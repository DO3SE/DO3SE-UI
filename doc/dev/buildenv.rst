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

1.  Follow the instructions for :file:`DO3SE_buildenv_GUI`, but instead using a directory called 
    :file:`DO3SE_buildenv_GUI` (the rest of the instructions assume :file:`C:\\DO3SE_buildenv_GUI`).
2.  Download the latest MinGW_ "Automated installer".  Run it and install to 
    :file:`C:\\DO3SE_buildenv_GUI\\MinGW`.
3.  Download the latest release of Python_ 2.6 (as of writing, there is no NumPy build for 2.7 and 
    the DO3SE GUI is not compatible with Python 3).  Install to 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26`.
4.  Download the latest Python 2.6 release of NumPy_.  Run the installer; it should autodetect where 
    to install if you only have one installation of Python on your system, but make sure the one it 
    has detected is in your :file:`DO3SE_buildenv_GUI` directory.
5.  Download the latest :guilabel:`win32-unicode` Python 2.6 release of wxPython_.  Run the 
    installer; it should automatically detect where to install, which will be a path like 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26\\Lib\\site-packages`.  If it is incorrect, change the 
    part before :file:`Python26` to be your :file:`DO3SE_buildenv_GUI` directory.
6.  Download the latest version of py2exe_ which ends in :file:`.win32-py2.6.exe`.  Run the 
    installer; the process should be identical to that for NumPy.
7.  If you have not already done so, copy :file:`resources/buildenv.bat` from the DO3SE source 
    directory to :file:`C:\\DO3SE_buildenv_GUI`.
8.  Bundle up the :file:`DO3SE_buildenv_GUI` directory in the same way as :file:`DO3SE_buildenv_F`.


.. _G95: http://www.g95.org/downloads.shtml
.. _MSYS: http://sourceforge.net/downloads/mingw/MSYS/BaseSystem/
.. _MinGW: http://sourceforge.net/downloads/mingw/Automated%20MinGW%20Installer/
.. _Python: http://python.org/download/releases/
.. _NumPy: http://sourceforge.net/projects/numpy/files/NumPy/
.. _wxPython: http://www.wxpython.org/download.php#binaries
.. _py2exe: http://sourceforge.net/projects/py2exe/files/
.. _7-zip: http://www.7-zip.org/
