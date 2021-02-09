These CLI tools depend on the do3se fortran and python code being built.
To do this follow the instructions in the main README.md file to build the
fortran code and install python dependencies. Then follow the steps below:

With your python virtual environment activated run `pip install -e .`. This will install
pydo3se locally.

You can then run the scripts with `python <scriptname> <options> <commands>`.
E.g. `python tools/convert_do3se_project_file_to_json.py example_do3se_config.do3se`

# Warning
If you make changes to the do3se src files (Python or Fortran) these will not be
updated for tool use until you run `pip install -e .`