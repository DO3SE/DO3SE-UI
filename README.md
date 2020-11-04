
# Dependencies

- Numpy
- wxPython # Install from website
- libSDL2-2.0.so.0 # install with sudo apt-get
- future # install with pip

# Build

- make py_ext

# Troubleshooting:
 - py2exe is depreciated. Use python >3.4

 - wxpython failing to build on ubuntu
   - `apt-get install build-essentials`
   - `pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython`
<!-- TODO: Check this is all in full docs -->
