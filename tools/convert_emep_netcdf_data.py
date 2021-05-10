#!/usr/bin/env python3
"""Convert EMEP NetCDF data to a format usable by DO3SE.

# Additional requirements
- click
- matplotlib
- numpy
- xarray (Also requries `pandas`, `netcdf4-python` `h5py`) `pip install "xarray[io]"`
- netcdf4-python (Follow instructions at github page)

This creates a coordinates csv file from the input data.
It pulls the emep data for each variable and merges them into per grid square annual files
where each row is an hour of data.
"""


# %%

import click
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


def get_dataset(var, data_directory, file_prefix, file_suffix):
    f = f'{data_directory}/{file_prefix}{var}{file_suffix}.nc'
    ds = xr.open_dataset(f)
    return ds


def generate_hourly_data_single_file(i, j, data_directory, datasets, variables, headings, save_output=True):
    output_filename = f'EMEP_CELL_{i}_{j}.csv'
    print(f'Creating file {output_filename} for variables {variables}')
    grid_cell_data = np.stack([get_hourly_data_for_var(
        ds, var, i, j) for ds, var in zip(datasets, variables)]).T
    if not save_output:
        return grid_cell_data
    with open(f'{data_directory}/converted_input_data/{output_filename}', 'w') as outfile:
        outfile.writelines([','.join(headings) + NEWLINE])
        outfile.writelines((','.join(line.astype(str)) + NEWLINE
                            for line in grid_cell_data))


def generate_gridded_hourly_data_files(data_directory, variables, headings=None, i_min=53, i_max=119, j_min=0, j_max=131, file_prefix='hourly_', file_suffix="_2009"):
    # WARNING THIS WILL LOAD EVERYTHING INTO MEMORY
    headings = headings or variables
    datasets = [get_dataset(var, data_directory,
                            file_prefix, file_suffix) for var in variables]
    try:
        os.makedirs(f'{data_directory}/converted_input_data')
    except OSError:
        pass

    for i in range(i_min, i_max):
        for j in range(j_min, j_max):
            generate_hourly_data_single_file(
                i, j, data_directory, datasets, variables,  headings)


@click.group()
def cli():
    click.echo("Using convert emep netcdf data tool")


@cli.command()
@click.option('--i_min', default=0, help="Min i coord")
@click.option('--i_max', default=119, help="Max i coord")
@click.option('--j_min', default=0, help="Min j coord")
@click.option('--j_max', default=131, help="Max j coord")
@click.argument('input_directory')
@click.argument('file_prefix')
@click.argument('file_suffix')
def run(
    input_directory: str,
    file_prefix: str,
    file_suffix: str,
    i_min,
    i_max,
    j_min,
    j_max,
):
    # i_min, i_max, j_min, j_max = grid // TODO: Get grid from args
    files = [f for f in os.listdir(
        input_directory) if f.split('.')[-1] == 'nc']
    variables = [f.replace(file_prefix, '').replace(
        file_suffix, '').replace('.nc', '') for f in files]
    print(variables)
    generate_gridded_hourly_data_files(
        input_directory,
        variables,
        file_prefix=file_prefix,
        file_suffix=file_suffix,
        i_min=i_min,
        i_max=i_max,
        j_min=j_min,
        j_max=j_max,
    )


if __name__ == "__main__":
    cli()
    # print("Running test run")
    # # Test run
    # generate_gridded_hourly_data_files(
    #     './tests/emep', ['Precip', 't2m'], ['precip', 'tsc'], 0, 5, 0, 5)
