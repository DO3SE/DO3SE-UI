.. vim: fo=aw2tq tw=100

======================================
Building the DOSE model User Interface
======================================

.. contents::

Windows
=======

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

8.  Go to the `MinGW download`_ site and download the latest version of the Automated MinGW
    Installer

9.  Run the MinGW installer, selecting only a "Minimal" install and using the ``C:\MinGW`` directory

10. From the `G95 download`_ site, download the "Self-extracting Windows x86" version of the G95 
    Fortran compiler

11. Run the G95 installer, installing to ``C:\MinGW`` - answer "Yes" when prompted about setting the 
    ``PATH`` and ``LIBRARY_PATH`` variables

12. From the `Python download`_ site, download the latest Python Windows Installer, and run it, 
    installing to the default location.  Pay attention to the directory it uses!

13. Add Python to your environment:

    1.  Open the Windows Control Panel
    2.  Open "System Properties"
    3.  Click on the "Advanced" tab
    4.  Click "Environment Variables"
    5.  Click on the "Path" system variable
    6.  Click "Edit"
    7.  Add a semicolon followed by the directory Python was installed in (e.g. ``...;c:\Python25``)

14. From the `Numerical Python download`_ site, download the latest version of the NumPy installer 
    that ends in ".win32-py2.5.msi" and run it - it should automatically get the correct directory 
    to install into

    * **Note:** The 1.0.4 version is broken (`bug on f2py mailing list`_)

15. From the `wxPython download`_ site, download the "win32-unicode" version of wxPython for Python 
    2.5 and install it - the default installation should be fine



.. _Cygwin: http://www.cygwin.com/
.. _setup.exe: http://www.cygwin.com/setup.exe
.. _FortranTools_windows_F.zip: ftp://ftp.swcp.com/pub/walt/F/FortranTools_windows_F.zip
.. _MinGW download: http://sourceforge.net/project/showfiles.php?group_id=2435&package_id=240780
.. _G95 download: http://ftp.g95.org/
.. _Python download: http://www.python.org/download/
.. _Numerical Python download: http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=175103
.. _bug on f2py mailing list: http://cens.ioc.ee/pipermail/f2py-users/2007-November/001487.html
.. _wxPython download: http://wxpython.org/download.php#binaries
