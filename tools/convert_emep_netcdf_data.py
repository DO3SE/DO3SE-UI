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


def get_spatial_annual_mean(ds, var):
    x = ds[var].values   # shape will be (8784, 120, 132) (hours, x, y)
    annual = np.mean(x, axis=0)
    return annual


def get_lat_long_values(ds):
    lons = ds['lon'].values
    lats = ds['lat'].values
    return lats, lons


def plot_spatial_mean(var, spatial_annual_mean):
    plt.pcolormesh(spatial_annual_mean)
    plt.colorbar()
    plt.title('Annual ' + var)
    plt.show()


def analyse_data():
    data_directory = './tests/emep'
    required_vars = 't2m SMI_deep Precip'.split()
    i = 58
    j = 12  # dbg, location in Spain
    for var in required_vars:
        f = f'{data_directory}/hourly_{var}.nc'
        ds = xr.open_dataset(f)
        lats, lons = get_lat_long_values(ds)
        spatial_annual_mean = get_spatial_annual_mean(ds, var)

        plot_spatial_mean(spatial_annual_mean)
        # print('Debug ', var, lons[j, i], lats[j, i], np.min(x), np.max(x))

        hourly_data = get_hourly_data_for_var(ds, var, i, j)
        plt.plot(hourly_data)
        plt.show()


def generate_coordinate_file(example_input_file, data_directory, i_min=0, i_max=119, j_min=0, j_max=131):
    ds = xr.open_dataset(example_input_file)
    lats, lons = get_lat_long_values(ds)
    rows = []
    jsondata = {}
    print(i_max)
    for i in range(i_min, i_max):
        for j in range(j_min, j_max):
            lat = lats[i, j]
            lon = lons[i, j]
            jsondata[f'{i}_{j}'] = [float(lat), float(lon)]
            # TODO: Check we have i and j correct way around
            rows.append(f'{i},{j},{lat},{lon}' + NEWLINE)

    with open(f"{data_directory}/coordinates.csv", 'w') as outfile:
        outfile.write('x,y,lat,lon' + NEWLINE)
        outfile.writelines(rows)
    with open(f"{data_directory}/coordinates.json", 'w') as outfile:
        json.dump(jsondata, outfile)


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
    generate_coordinate_file(
        f'{data_directory}/{file_prefix}{vars[0]}.nc', data_directory, i_min, i_max, j_min, j_max)
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
    input_directory, file_prefix, *grid = args
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
