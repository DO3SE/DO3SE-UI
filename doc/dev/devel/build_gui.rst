Building and running the GUI
============================

:Author: Alan Briolat <sei@alanbriolat.co.uk>

To run the GUI, two parts of it must be generated from source files:  the Python extension module 
built from the Fortran code (see :mod:`do3se.model`), and the resources module built from various 
additional files the GUI requires at run time (see :mod:`do3se.resources`).

To build everything, run::

    python build_resources.py
    make py_ext

If you get build errors that look like this::

    Fatal Error: File 'constants.mod' opened at (1) is not a GFORTRAN module file  
    F/functions.f90:80.43:

then you need to run ``make clean`` before ``make py_ext``; files left over from building the F 
model with G95 will cause this problem.

Once everything is built in this way, it should be possible to run the GUI with::

    python DO3SE.py


Windows executable
------------------

The py2exe_ utility is used to build a Windows executable, and it only runs on Windows.  To simplify 
the process of this build, a script is provided.  Running::

    sh build-gui-win32.sh

will build the executable and other required files into a directory (the name of which depends on 
the application version) and also compresses that directory into a zip file of the same name.  The 
name can be overridden by providing an argument to the script, for example::

    sh build-gui-win32.sh 2.0-beta4

will create the directory :file:`DO3SE-2.0-beta4` and the zip file :file:`DO3SE-2.0-beta4.zip`.  
Double clicking on the executable, or running :file:`DO3SE-2.0-beta4\DO3SE.exe` will launch the 
application.


.. _py2exe: http://www.py2exe.org/
