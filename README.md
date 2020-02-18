DO3SE - UI

The UI Repository seems to contain the official setup for creating the GUI DO3SE model.

---
# Notes
Setup is currently Fortran model to do the calculations with a Python GUI (wxpython) that sits on top. End user uses GUI to set model paramaters then load a dataset as input. The model is then ran and returns analytics output data to the GUI.

 - Written with https://wxpython.org/
 - For windows setup can use WSL (Windows subsystem with Ubuntu)? (CHECK THIS)

Addional Notes in `/doc/NOTES` & `/doc/STRUCTURE`

# Useful Links
 - SEI page - https://www.sei.org/projects-and-tools/tools/do3se-deposition-ozone-stomatal-exchange/
 - Github - https://github.com/SEI-DO3SE/DO3SE-UI
 - Creating a linux environment in Windows - https://docs.microsoft.com/en-us/windows/wsl/install-win10 
 - Science Stuff Documentation - Y:\Theme 1 MES\Projects\DO3SE Documentation\Documentation of DO3SE model_Ver15.docx

# Entry Points
These are possible entry points for building/running the model. These need checking.
- build-gui-win32?
- Makefile
- setup.py

# First time setup - Developers (Windows)

## Developer Requirements
Note: have not currently got this working on windows without using Linux subsystem

### All environments
1.  Setup ssh keys (https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account)
2. Python(2?) & PIP & virtualEnv *
2. An IDE (VSCode)


### Windows (NOT TESTED)
1. Git for windows
2. MinGw for windows - to run make files - https://sourceforge.net/projects/mingw/
3. Fortran Compiler - G95 - fortran.com/the-fortran-company-homepage/whats-new/g95-windows-download/

### Linux
1. make
    - Run `sudo apt-get update`
    - Run `sudo apt install make`
2. gfortran
    - Run `sudo apt install gfortran`
3. 

## Setup Steps
1. Clone DO3SE-UI master branch
2. setup venv with virtualenv then activate **
3. install python dependencies with `python -m pip install -r requirements.txt`
    - Note: wxpython requires specific build for linux (https://wxpython.org/pages/downloads/)


## Build
### Standalone (NOT TESTED)
1. Run `make dose` (Not sure what this makes yet!)

### PY_GUI
1. Run `make py_ext`


# OTHER

Building F module in Windows
----------------------------

+ Install python
+ Install numpy
+ Install mingw to C:\mingw
+ Install g95 to C:\mingw - *** say "yes" to changing the path *** (no to installing utilities)
+ python f2py.py -c --fcompiler=f95 --compiler=mingw32

# Apendix
- \* Install python(2) with `sudo apt install python` then setup a symlink `ln -s /usr/bin/python/python2.7 /usr/bin/python/python`. This will make python on the command line point to python 2.7. Install pip with `sudo apt install python-pip` and virtual env with `python -m pip install virtualenv`
- ** To create a a virtual environment (Python 2) in the project root run `python -m virtualenv venv` then activate it with `source venv/bin/activate` this will now activate the virtual enviornment and anything installed with pip will install here rather than globally


