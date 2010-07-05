Ftools -- Building F programs on Windows made easy
==================================================

Trying to install all the necessary components to build F programs on Windows is awkward for 
anybody, and worse for a non-developer.  To take the hassle out of this, it is possible to build a 
zipfile which contains all of the necessary tools that requires no setup to run.  Simply unzip it, 
double click on :file:`Ftools.bat`, and then use the tools as normal.


How to use the bundle
---------------------

1.  Unzip the bundle somewhere.
2.  Run the contained :file:`Ftools.bat`.
3.  Use the F compiler as you usually would.
   
It's that simple.  No searching for all the parts, no installation, no messing with environment 
variables.


How to make an Ftools bundle
----------------------------

1.  Download the MinGW_ automated installer and run it.  Do a minimal install to 
    :file:`C:\\Ftools\\MinGW`.
2.  Download the G95_ "Self-extracting Windows x86" installer and run it.  Install to 
    :file:`C:\\Ftools\\MinGW`.  Do not allow it to set environment variables.
3.  Download the MSYS_ base system installer and run it (version 1.0.11, later versions do not have 
    an installer as of writing).  Install to :file:`C:\\Ftools\\msys\\1.0`.
4.  Copy :file:`F.bat` and :file:`Ftools.bat` (from the :file:`Ftools` directory in the DO3SE source 
    code) into :file:`C:\\Ftools`.
5.  ZIP the :file:`C:\\Ftools` directory and distribute it.


.. _MinGW: http://sourceforge.net/downloads/mingw/Automated%20MinGW%20Installer/
.. _G95: http://www.g95.org/downloads.shtml
.. _MSYS: http://sourceforge.net/downloads/mingw/MSYS/BaseSystem/
