=========================================
Ftools - A bundle for building F programs
=========================================

How to make an Ftools bundle
============================

Trying to install all the necessary components to build F programs is a pain, and to do it over and
over again even moreso.  A better way is to make a bundle that contains everything that is needed.

1.  Download MinGW automated installer and run it.  Do a minimal install to C:\Ftools\MinGW
2.  Download G95 installer and run it.  Install to C:\Ftools\MinGW.  Do not allow it to set
    environment variables.
3.  Download MSYS installer and run it (version 1.0.11, later versions do not have an installer as
    of writing).  Install to C:\Ftools\msys\1.0.
4.  Copy the .bat files from this directory into C:\Ftools.
5.  ZIP the C:\Ftools directory and distribute it.


How to use the bundle
=====================

1.  Unzip the bundle somewhere.
2.  Run the contained Ftools.bat.
3.  Use the F compiler as you usually would, only without the need to have installed anything!
