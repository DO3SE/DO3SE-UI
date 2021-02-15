#!/usr/bin/env python3
"""Convert EMEP NetCDF data to a format usable by DO3SE.

# Additional requirements
- matplotlib
- numpy
- xarray (Also requries `pandas`, `netcdf4-python` `h5py`) `pip install "xarray[io]"`
- netcdf4-python (Follow instructions at github page)

This creates a coordinates csv file from the input data.
It pulls the emep data for each variable and merges them into per grid square annual files
where each row is an hour of data.
"""


# %%

import sys
import os
import numpy as np
import xarray as xr
import json
NEWLINE = '\n'


def get_hourly_data_for_var(ds, var, i, j):
    x = ds[var].values   # shape will be (8784, 120, 132) (hours, x, y)
    # print('P', var, np.shape(x), x.ndim)  # 24, 120, 132
    hourly_data = x[:, i, j]
    return hourly_data


def get_dataset(var, data_directory, file_prefix):
    f = f'{data_directory}/{file_prefix}{var}.nc'
    ds = xr.open_dataset(f)
    return ds


def generate_gridded_hourly_data_files(data_directory, vars, headings=None, i_min=0, i_max=119, j_min=0, j_max=131, file_prefix='hourly_'):
    # WARNING THIS WILL LOAD EVERYTHING INTO MEMORY
    headings = headings or vars
    datasets = [get_dataset(var, data_directory, file_prefix) for var in vars]
    try:
        os.makedirs(f'{data_directory}/converted_input_data')
    except OSError:
        pass

    for i in range(i_min, i_max):
        for j in range(j_min, j_max):
            output_filename = f'EMEP_CELL_{i}_{j}.csv'
            print(f'Creating file {output_filename} for vars {vars}')
            grid_cell_data = np.stack([get_hourly_data_for_var(ds, var, i, j)
                                       for ds, var in zip(datasets, vars)]).T
            with open(f'{data_directory}/converted_input_data/{output_filename}', 'w') as outfile:
                outfile.writelines([','.join(headings) + NEWLINE])
                outfile.writelines((','.join(line.astype(str)) + NEWLINE
                                    for line in grid_cell_data))


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        input_directory, file_prefix = args
        elevation_file = None
    else:
        raise ValueError(
            'Invalid args. Should be input_directory, file_prefix')

    # i_min, i_max, j_min, j_max = grid // TODO: Get grid from args
    files = [f for f in os.listdir(
        input_directory) if f.split('.')[-1] == 'nc']
    vars = [f.replace(file_prefix, '').replace('.nc', '') for f in files]
    print(vars)
    generate_gridded_hourly_data_files(
        input_directory, vars, file_prefix=file_prefix)

# %%
# Test run
# generate_gridded_hourly_data_files(
#     './tests/emep', ['Precip', 't2m'], ['precip', 'tsc'], 0, 5, 0, 5)
