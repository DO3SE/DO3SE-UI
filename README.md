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

- `make py_ext` for python
- `make py_cli` for python cli only
- `make dose` for fortran only

# Running Cli

- Run `make py_cli`
- Run `python DO3SE_cli.py -c json -o [OUTFILE] [CONFIG_FILE] [INPUT_FILE]`

# Troubleshooting

- py2exe is depreciated. Use python >3.4

- \_model module not found. This must be built using python setup.py build_ext then copied to the do3se directory

- wxpython failing to build on ubuntu
  - `apt-get install build-essentials`
  - `pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython`
- wxpython missing dependencies on linux. Check extra dependencies installed: https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites

- Make sure to run `make py_cli` after making any fortran changes
