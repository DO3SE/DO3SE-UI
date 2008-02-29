.. vim: fo=aw2tq tw=100

=================================
Building the DOSE model - Windows
=================================

.. contents::

Just the F model
================

Preparing the environment
-------------------------

1.  Download and run setup.exe_ from the Cygwin_ website.

2.  Select the "Archive -> unzip" and "Devel -> make" packages.  **Note:** Do not install Python or 
    MinGW from this screen

3.  Click "Next" and let it install the packages - this may take a while!

4.  Run the Cygwin shell once to make sure your "home" directory gets created

5.  Download FortranTools_windows_F.zip_ from the FortranTools FTP server into your Cygwin home 
    directory (e.g. ``C:\cygwin\home\your_username``)

6.  Open the Cygwin shell

7.  Run the following to unpack and install the F compiler::

      unzip FortranTools_windows_F.zip
      cd FortranTools
      sed "s/\r//g" install_fortrantools > install_fortrantools.fixed
      ./install_fortrantools.fixed

.. _Cygwin: http://www.cygwin.com/
.. _setup.exe: http://www.cygwin.com/setup.exe
.. _FortranTools_windows_F.zip: ftp://ftp.swcp.com/pub/walt/F/FortranTools_windows_F.zip

Building the model
------------------

1.  Unzip the source code somewhere

2.  Take a look at ``F\dose.f90`` to see the filename that should be used for the input file (and 
    what filename to expect for the output file)

3.  Open a Cygwin shell and change directory to where the source code is

4.  Run the ``make`` command - the compiled program will be called ``dose``


The User Interface
==================

Preparing the environment
-------------------------

1.  From the `Python download`_ site, download the latest Python Windows Installer and run it, 
    paying attention to the path it installs into (for example ``C:\Python25``)

2.  Add Python directory to your environment:

    1.  Open the Windows Control Panel
    2.  Open "System Properties"
    3.  Click on the "Advanced" tab
    4.  Click "Environment Variables"
    5.  Click on the "Path" system variable
    6.  Click "Edit"
    7.  Add a semicolon followed by the directory Python was installed in (e.g. ``;c:\Python25``)

3.  From the `Numerical Python download`_ site, download the latest version of the NumPy Windows 
    installer (ending in ``.win32-py2.5.msi``) and run it - it should automatically choose the 
    correct installation directory

    * **Note:** The 1.0.4 version is broken (`bug on f2py mailing list`_)

4.  From the `wxPython download`_ site, download and install the "win32-unicode" version of wxPython 
    for Python 2.5


5.  Go to the `MinGW download`_ site and download the latest version of the Automated MinGW
    Installer

6.  Run the MinGW installer, selecting only a "Minimal" install and using the ``C:\MinGW`` directory

7.  From the `G95 download`_ site, download the "Self-extracting Windows x86" version of the G95 
    Fortran compiler

8.  Run the G95 installer, installing to ``C:\MinGW`` - answer "Yes" when prompted about setting the 
    ``PATH`` and ``LIBRARY_PATH`` variables

9.  From the `py2exe download`_ site, download the latest version of the py2exe installer (ending in 
    ``.win32-py2.5.exe``) and run it

.. _MinGW download: http://sourceforge.net/project/showfiles.php?group_id=2435&package_id=240780
.. _G95 download: http://ftp.g95.org/
.. _Python download: http://www.python.org/download/
.. _Numerical Python download: http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103
.. _bug on f2py mailing list: http://cens.ioc.ee/pipermail/f2py-users/2007-November/001487.html
.. _wxPython download: http://wxpython.org/download.php#binaries
.. _py2exe download: http://sourceforge.net/project/showfiles.php?group_id=15583


Building the application
------------------------

1.  Extract the DOSE source code somewhere

2.  Open a Windows command prompt (Start menu -> Run..., type "cmd", click OK)

3.  Change to the directory the program is in (using "``cd``")

4.  Run the following::

        python setup.py py2exe
        python fix-dlls.py

5.  Go to the "``dist``" directory under where you unpacked the DOSE source code (either in Windows 
    Explorer or the command prompt) and run ``dose-ui.exe``



