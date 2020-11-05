

<!-- TODO: Check this is all in full docs -->

# Dependencies

- Numpy
- wxPython # Install from website
- libSDL2-2.0.so.0 # install with sudo apt-get
- future # install with pip

- If running with a headless ubuntu setup (Docker/WSL etc) then additional dependencies may need to be installed.
```
apt-get install freeglut3-dev \
libgl1-mesa-dev \
libglu1-mesa-dev \
libgstreamer-plugins-base1.0-dev \
libgtk-3-dev \
libjpeg-dev \
libnotify-dev \
libpng-dev \
libsdl2-dev \
libsm-dev \
libtiff-dev \
libwebkit2gtk-4.0-dev \
libxtst-dev
```

# Build

- make py_ext


# Troubleshooting
 - py2exe is depreciated. Use python 3.4

 - _model module not found. This must be built using python setup.py build_ext then copied to the do3se directory

- wxpython missing dependencies on linux. Check extra dependencies installed: https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites