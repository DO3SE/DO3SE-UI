Build Environment (Windows)
===========================

:Author: Alan Briolat <sei@alanbriolat.co.uk>

To build either the F code or the GUI on Windows, there are several dependencies that must be 
installed.  Going through the process of installing them is quite a lengthy and potentially 
error-prone process, so this document instead focusses on the method for creating build environment 
"bundles" which can be redistributed, extracted and used without any further effort.  Many of the 
installers used to create the bundle require Administrator privileges, however the final product 
will not.

These instructions assume you have access to the full DO3SE source (not just the F code) when 
building the environment, since it contains various files required to make the build environment 
work.


:file:`DO3SE_buildenv_F` -- Minimal Fortran90/F build environment
-----------------------------------------------------------------

Building any F program requires the G95 Fortran compiler.  To build the DO3SE F model, GNU Make is 
also required to use the Makefile which contains instructions for building the model from several 
source files.  GNU Make and associated utilities are provided by MSYS.

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

.. note::

    :file:`buildenv.bat` has a version-specific path hard-coded (``...\4.0.4\...``); this will need 
    to be changed if G95 starts using a different version of GCC.  When attempting to compile an F 
    file with ``F somefile.f90``, the error :guilabel:`g95: installation problem, cannot exec 
    'f951': No such file or directory` will indicate that this has become a problem.


:file:`DO3SE_buildenv_GUI` -- Full GUI build environment
--------------------------------------------------------

Building the GUI requires a lot more dependencies than just building the F model, and also a 
different Fortran compiler.  For this reason, a different build environment bundle is created.  This 
bundle still includes all the tools required to build the F model.

* Python -- The GUI is written in Python, therefore the Python interpreter is required to run it.
* wxPython -- The library used to create the GUI.
* NumPy -- Contains the utilities necessary for integrating the F model into the Python GUI.
* MinGW -- Compiler collection needed by NumPy to create the wrapper that allows integration with 
  the F model.
* py2exe -- Allows the Python GUI to be bundled into a single executable.
* 7-zip -- A small archiving utility for bundling up the built GUI.

1.  Create a :file:`DO3SE_buildenv_GUI` directory somewhere (the rest of the instructions will 
    assume :file:`C:\\DO3SE_buildenv_GUI`).
2.  Download and run the latest stable "Self-extracting Windows x86" installer for G95_, installing 
    to :file:`C:\\DO3SE_buildenv_GUI\\g95`.

    * When prompted :guilabel:`Install MinGW utilities and libs?` click :guilabel:`Cancel`.
    * When prompted :guilabel:`Set PATH = ...` click :guilabel:`Cancel`.
      
3.  Download and run the latest MinGW_ automated installer (e.g.  
    :file:`mingw-get-inst-20100909.exe`), installing to :file:`C:\\DO3SE_buildenv_GUI\\MinGW`.  At 
    the :guilabel:`Select Components` screen, select :guilabel:`Fortran Compiler` and 
    :guilabel:`MSYS Basic System`.

    * Once MinGW is installed, delete the :file:`C:\\DO3SE_buildenv_GUI\\MinGW\\var` directory; it 
      contains a lot of big files required only during installation.

4.  Download the latest release of Python_ 2.6 (as of writing, there is no NumPy build for 2.7 and 
    the DO3SE GUI is not compatible with Python 3).  Install to 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26`.  **It is essential that you select "Install just for 
    me" otherwise the bundle will not work on another computer.** [#novcredist]_
5.  Download the latest Python 2.6 release of NumPy_.  Run the installer; it should autodetect where 
    to install if you only have one installation of Python on your system, but make sure the one it 
    has detected is in your :file:`DO3SE_buildenv_GUI` directory.
6.  Download the latest :guilabel:`win32-unicode` Python 2.6 release of wxPython_.  Run the 
    installer; it should automatically detect where to install, which will be a path like 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26\\Lib\\site-packages`.  If it is incorrect, change the 
    part before :file:`Python26` to be your :file:`DO3SE_buildenv_GUI` directory.
7.  Download the latest version of py2exe_ which ends in :file:`.win32-py2.6.exe`.  Run the 
    installer; the process should be identical to that for NumPy.
    
    * If the installer fails to run, you may need to install the "Microsoft Visual C++ 2008 
      Redistributable" which can be `downloaded here 
      <http://www.microsoft.com/downloads/details.aspx?FamilyID=9b2da534-3e03-4391-8a4d-074b9f2bc1bf&displaylang=en>`_.

8.  Download the `7-Zip Command Line Version`_ and unzip it somewhere.  Copy the :file:`7za.exe` 
    into your :file:`DO3SE_buildenv_GUI` directory.
9.  Copy :file:`resources/buildenv.bat` from the DO3SE source directory to 
    :file:`C:\\DO3SE_buildenv_GUI`.
10. Copy the :file:`resources/Microsoft.VC90.CRT` directory from the DO3SE source directory to 
    :file:`C:\\DO3SE_buildenv_GUI\\Python26\\Lib\\site-packages\\wx-2.8-msw-unicode\wx` and to 
    :file:`site-packages\\py2exe`.  [#novcredist]_
11. Bundle up the :file:`DO3SE_buildenv_GUI` directory in the same way as :file:`DO3SE_buildenv_F`.


Using a build environment
-------------------------

To use a build environment, simply unpack it somewhere and run the contained :file:`buildenv.bat`.  
This batch script sets up the environment variables such that all the required tools are accessible 
from within the console session that is launched.


.. [#novcredist] Necessary to remove dependency on having Visual C++ redistributable installed.


.. _G95: http://www.g95.org/downloads.shtml
.. _MSYS: http://sourceforge.net/downloads/mingw/MSYS/BaseSystem/
.. _MinGW: http://sourceforge.net/downloads/mingw/Automated%20MinGW%20Installer/mingw-get-inst/
.. _Python: http://python.org/download/releases/
.. _NumPy: http://sourceforge.net/projects/numpy/files/NumPy/
.. _wxPython: http://www.wxpython.org/download.php#binaries
.. _py2exe: http://sourceforge.net/projects/py2exe/files/
.. _7-zip: http://www.7-zip.org/
.. _7-Zip Command Line Version: http://www.7-zip.org/download.html
