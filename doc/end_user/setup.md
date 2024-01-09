# DO3SE UI End User Setup

# Using packaged wheel

1. install the latest wheel `pip install do3se-3.6.38-cp38-cp38-linux_x86_64.whl`

# Using the source code

1. Set the `BUILD_ROOT` environment variable to the root of the source code
2. Run `python setup.py build`
3. Run `python -m pip install -e $BUILD_ROOT`
