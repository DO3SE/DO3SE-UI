# DO3SE Grid Runs

An example grid run setup can be found in `tests/gridrun`

The `configs` folder contains do3se parameter files. Each file will be run on the entire grid.

The `e_state_overrides.nc` file contains config overrides per cell. E.g. latitude and longitude.

The `inputs` directory contains input netcdf files. Currently the model only supports
inputs shown in the same format as the example. I.e. a file per variable.

The `coords.csv` file contains a list of index coordinates to run.

## Running the example

Edit the `grid_run_test.py` file to change the run_id. Run the `grid_run_test.py` file.
Outputs should be saved in the `outputs/` directory.