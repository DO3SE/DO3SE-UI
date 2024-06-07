# DO3SE UI End User Setup

## Install dependencies

'numpy==1.24.4',
'future',
'pandas',



## Using packaged wheel

1. install the latest wheel `pip install wheel do3se-3.6.46-cp38-cp38-linux_x86_64.whl`

## Using the source code

1. Install build dependencies `python3 -m pip install --upgrade build`
1. Set the `BUILD_ROOT` environment variable to the root of the source code
2. Run `python setup.py build`
3. Run `python -m pip install -e $BUILD_ROOT`
