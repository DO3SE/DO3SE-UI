# DO3SE Installation

## Dependencies

`pip install -r requirements/common.txt`
For grid runs also run `pip install -r requirements/gridruns.txt`

## Build

- `make py_ext` for python
- `make py_cli` for python cli only
- `make dose` for fortran only

or...

`python -m build`


## Install DO3SE

Finally install do3se with `pip install -e .` from the root of this repo.

## Check working

### Single Run

...

### Batch Run

...

### Grid runs

run `python tests/gridrun/grid_run_test.py`.
Output should be located in `tests/gridrun/outputs`
Additional grid run docs can be found in `doc/end_user/grid_runs.md`

## Running Cli

- Run `make py_cli`
- Run `python -m DO3SE_cli --help`

<!-- Legacy setup -->
<!-- - Run `python DO3SE_cli.py -c json -o [OUTFILE] [CONFIG_FILE] [INPUT_FILE]` -->

## Deployment

To deploy to HPC machines run
`pip install git+ssh://git@github.com/SEI-DO3SE/DO3SE-UI@master`

## Troubleshooting

- py2exe is depreciated. Use python >3.4

- \_model module not found. This must be built using python setup.py build_ext then copied to the do3se directory

- wxpython failing to build on ubuntu
  - `apt-get install build-essentials`
  - `pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04 wxPython`
- wxpython missing dependencies on linux. Check extra dependencies installed: https://github.com/wxWidgets/Phoenix/blob/master/README.rst#prerequisites

- Make sure to run `make py_cli` after making any fortran changes
