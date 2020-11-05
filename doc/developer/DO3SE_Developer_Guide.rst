Development Environment
=======================

To build any of the software, at the very least the software the build
system is based on and the dependencies for the software must be
present.

The build system is a collection of “Makefiles”, as used by GNU Make.
Therefore any platform on which the software is to built must have GNU
Make installed.

To build the F model, a Fortran compiler which understands the F
standard is needed. Currently the only freely-available such compiler is
G95, which is built on GCC (the GNU Compiler Collection), therefore both
GCC and G95 must be installed in some form to build the F model.

The GUI (Graphical User Interface) is written in the Python programming
language, using the wxWidgets cross-platform GUI toolkit. The bridge
between Python and the F model is created by F2PY (Fortran-to-Python)
which is part of the NumPy (Numerical Python) library. The full
dependencies are:

-  A working environment for building the F model

-  Python :math:`>=` 2.5 (but not Python 3.x)

-  NumPy :math:`>=` 1.1.0

-  wxWidgets 2.8

-  wxPython 2.8 (the Python bindings for wxWidgets)

The following sections describe how to install the necessary
dependencies for both software builds on common platforms.

Preparing a Windows Environment
-------------------------------

F Model Dependencies
~~~~~~~~~~~~~~~~~~~~

G95 for Windows depends on MinGW (“Minimalist GNU for Windows”) to
provide GCC. GNU Make is provided by MSYS [1]_ (“Minimal System”), a
basic Linux-like environment for Windows.

Installing MinGW
^^^^^^^^^^^^^^^^

#. Download and run the latest Automated MinGW Installer from the —click
   on “Automated MinGW Installer” and then on the latest ``.exe`` file,
   e.g. ``MinGW-5.1.4.exe``.

#. Click through the installer; the options are self-explanatory in most
   cases.

#. When given a choice of which components to install, the “Minimal”
   install is sufficient. Select additional features if desired.

#. When asked for a “Destination Folder”, use ``C:\MinGW``

#. Click “Install” and wait for the necessary files to be downloaded and
   installed. This will probably take a few minutes on a fast Internet
   connection.

Installing G95
^^^^^^^^^^^^^^

#. Navigate to the , click on the most recent “Stable Version” link.

#. Download the installer by clicking one of the links next to
   “Self-extracting Windows x86” and run it.

#. Make sure the “Destination Folder” is the same as where MinGW was
   installed to (``C:\MinGW``) and click “Install”, then click “Yes”
   when notified that it will install into the MinGW directory
   structure.

#. When asked about setting ``PATH`` and ``LIBRARY_PATH`` variables, it
   is not essential to answer “OK” here, but may be desirable—adding the
   “bin” directory to the ``PATH`` variable removes the need to use the
   full path to the compilers when using them for other projects.

Installing MSYS
^^^^^^^^^^^^^^^

#. Download and run the MSYS Base System installer from the —click on
   “MSYS Base System”, then “Current Release”, then the ``.exe`` file,
   e.g. ``MSYS-1.0.10.exe``.

#. Click through the installer; the options are self-explanatory in most
   cases.

#. When asked for a “Destination Directory”, use ``C:\msys\1.0``

#. In the command prompt window that appears after installing MSYS, it
   is safe to answer “n” to skip the post-install process.

#. It’s probably undesirable to read all the technical documents that
   come with MSYS at this point, so uncheck the two boxes on the final
   screen before clicking “Finish”.

Adding MSYS to the PATH Variable (Optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It may be desirable to add MSYS to the ``PATH`` environment variable so
it is not necessary to use the full path to ``make`` when running the
build system.

#. Open the “System Properties” dialog, for example by pressing the
   “Win+Break” key combination or right-clicking on “My Computer” and
   clicking “Properties”.

#. Click the “Advanced” tab, and then the “Environment Variables”
   button.

#. If the ``PATH`` variable already exists in the “User variables”
   section, click it and click “Edit”, otherwise click “New” and use
   ``PATH`` as the variable name.

#. Add the path to the MSYS binary path to the value (prefixing it with
   a semicolon—“;”—if a value already exists). The MSYS binary path
   should look something like ``c:\msys\1.0\bin``.

GUI Dependencies
~~~~~~~~~~~~~~~~

Before installing the GUI dependencies, it is necessary to install the F
model dependencies first. You *should* follow all instructions for
adding to the ``PATH`` environment variable in the guide for installing
the F model dependencies.

#. From the , download and run the “Python 2.x.x Windows installer”
   (where 2.x.x is the version number, e.g. 2.6.2).

#. Install Python with the default settings, but make a note of the
   installation directory, e.g. ``C:\Python26``.

#. Edit the ``PATH`` variable (as described above) and add the Python
   installation directory noted in the previous step.

#. Navigate to the , expand the folder for the latest version, and
   download the version that matches your platform and Python version.
   For Windows, the filename will contain ``win32``, and for Python 2.6
   it will end with ``python2.6.exe``.

#. Run the NumPy installer and click through it—it will install the
   necessary files to the correct location after automatically detecting
   where Python was installed.

#. From the , download and run the installer appropriate to the version
   of Python that was installed (use the installer ending in
   ``-unicode``, not ``-ansi``). Yet again, just click through the
   installer.

#. From the , download and install the version of py2exe appropriate to
   your platform—for example, for Python 2.6 the filename will contain
   ``-py2.6``.

Preparing a Linux Environment
-----------------------------

F Model Dependencies
~~~~~~~~~~~~~~~~~~~~

Building the F model on a Linux system requires the presence of both GNU
Make and G95 (which in turn depends on GCC). Make and GCC can usually be
installed via the package manager, using the “make” and “gcc” packages.
(If you are using a distribution which does not have these packages, you
most likely know how to build them yourself.)

Installing G95
^^^^^^^^^^^^^^

#. Navigate to the , click on the most recent “Stable Version” link.

#. Download the “Linux x86” version if you are running 32-bit Linux, or
   a “Linux x86\_64/EMT64” version if you are running 64-bit Linux. If
   you do not know which you are running, run ``uname -m`` (i686 is
   32-bit, x86\_64 is 64-bit).

#. Unpack the files, which should create a ``g95-install`` directory:

   ::

       $ tar xzf g95-x86-linux.tgz

   Or, to put it somewhere more permanent,

   ::

       $ tar xzf g95-x86-linux.tgz -C /opt/

#. Create a symbolic link for the ``g95`` binary (the filename will be
   different for 64-bit, but there will be only one file in
   ``g95-install/bin``):

   ::

       $ ln -s /opt/g95-install/bin/i686-pc-linux-gnu-g95 /usr/local/bin/g95

#. Check that G95 was installed correctly by attempting to run it:

   ::

       $ g95
       g95: no input files

GUI Dependencies
~~~~~~~~~~~~~~~~

The dependencies for building and running the GUI are specified in
[dev:env], and can usually be installed using your Linux distribution’s
package manager. The development files for Python are required to run
F2PY and are usually in a separate package, so this needs to be
installed even if Python is already installed. For example, under Ubuntu
or Debian:

::

    $ sudo apt-get install python-dev python-wxgtk2.8 python-numpy

In addition, the only Fortran compiler on Linux that appears to work
with F2PY correctly is ``gfortran``, so this also needs to be installed:

::

    $ sudo apt-get install gfortran

Building the Software
=====================

This section describes how to use the build system to build the software
in different environments, but not how to modify the software or set it
up to do something useful—this is covered in later sections. This is
because the build step varies between platforms, whereas modifying the
software does not.

It is assumed that a “zip file” containing the source code has already
been obtained and unzipped somewhere.

In a Windows Environment
------------------------

Building the F Model
~~~~~~~~~~~~~~~~~~~~

#. Open the Makefile from the source directory in a text editor and
   check that the ``WIN32_LIB_...`` and ``WIN32_BIN_...`` paths “look
   right” for how MinGW and MSYS was installed.

#. Open a Windows terminal prompt, for example by clicking the “Start”
   button and then “Run...” and typing ``cmd.exe``, and change directory
   into the directory that was extracted from the zip file. For example,
   if the zip file was ``DO3SE-src-F-20090620`` and was extracted to “My
   Documents”, your terminal session might look like this:

   ::

       C:\Documents and Settings\Alan>cd "My Documents\DO3SE-src-F-20090620"
       C:\Documents and Settings\Alan\My Documents\DO3SE-src-F-20090620>dir
       ...
       20/06/2009  18:53   <DIR>       .
       20/06/2009  18:53   <DIR>       ..
       20/06/2009  18:53   <DIR>       F
       20/06/2009  18:53               Makefile
       ...

   For Windows Vista and above, replace “Documents and Settings” and “My
   Documents” with “Users” and “Documents”.

#. Run ``make PLATFORM=win32`` to build the F model for 32-bit Windows.
   If MSYS was not added to the ``PATH``, supply the full path to the
   ``make`` executable:

   ::

       C:\...\DO3SE-src-F-20090620>c:\msys\1.0\make PLATFORM=win32

#. If there are no errors, the program ``dose.exe`` should have be
   created in the current directory.

   ::

       C:\Documents and Settings\Alan\My Documents\DO3SE-src-F-20090620>dir
       ...
       20/06/2009  18:53   <DIR>       .
       20/06/2009  18:53   <DIR>       ..
       20/06/2009  18:53   <DIR>       F
       20/06/2009  18:53               Makefile
       20/06/2009  18:56               dose.exe
       ...

Using the F Model—Quick Start
=============================

The F model, when built, is a stand-alone command-line program. To run
it, make sure there is an input file of the correct filename in the
current directory and then execute the program from the command line:

::

    C:\...\DO3SE-src-F-20090620>dir
    ...
    20/06/2009  18:53   <DIR>       .
    20/06/2009  18:53   <DIR>       ..
    20/06/2009  18:53   <DIR>       F
    20/06/2009  18:53               Makefile
    20/06/2009  18:56               dose.exe
    20/06/2009  18:56               input_newstyle.csv
    ...
    C:\...\DO3SE-src-F-20090620>dose.exe
    C:\...\DO3SE-src-F-20090620>dir
    ...
    20/06/2009  18:53   <DIR>       .
    20/06/2009  18:53   <DIR>       ..
    20/06/2009  18:53   <DIR>       F
    20/06/2009  18:53               Makefile
    20/06/2009  18:56               dose.exe
    20/06/2009  18:56               input_newstyle.csv
    20/06/2009  18:59               output.csv
    ...

Alternatively, double-click on ``dose.exe`` to run it—be aware that this
will hide any errors that might have been visible on the command line.

If the output file (``output.csv`` by default) is empty, it is most
likely that no output columns have been specified (see the next
section).

Configuring Input and Output
----------------------------

The input and output of the F model is configured in ``F/dose.f90``.

-  The input and output filenames are set near the bottom of the file,
   in the ``Run_DOSE`` section.

-  The columns to include in the output are set in the ``WriteData``
   subroutine. Uncomment a line to include that variable in the output.
   The variables and their meanings are documented in
   ``F/variables.f90``.

-  The input format is defined in the ``ReadData`` subroutine. *This
   should be used for guidance, but not modified.* The variables and
   their meanings are documented in ``F/inputs.f90``.

-  Where certain calculations have multiple implementations, these can
   be chosen between in the ``Calculate`` subroutine.

To change any of these options, edit ``F/dose.f90`` as necessary and
save it. To use the changes, rebuild the model (see [dev:build]) and run
it again. *If the output filename has not been changed and the previous
results have not been moved, they will be overwritten.*

.. [1]
   MinGW also provides Make, but does not have a full shell environment
   and therefore lacks important utilities.
