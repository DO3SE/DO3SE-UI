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
import xarray as xr
import json
NEWLINE = '\n'


def get_lat_long_values(ds):
    lons = ds['lon'].values
    lats = ds['lat'].values
    return lats, lons


def get_elevation_data(elevation_file):
    ds = xr.open_dataset(elevation_file)
    elev = ds['NWP_Elevation_in_m'][0].values
    return elev


def generate_coordinate_file(example_input_file, output_file_name, i_min=0, i_max=119, j_min=0, j_max=131, elevation_file=False):
    ds = xr.open_dataset(example_input_file)
    lats, lons = get_lat_long_values(ds)
    elevs = elevation_file and get_elevation_data(elevation_file)
    rows = []
    jsondata = {}
    for i in range(i_min, i_max):
        for j in range(j_min, j_max):
            lat = lats[i, j]
            lon = lons[i, j]
            elev = elevs[i, j] if elevation_file else 0
            key = f'{i}_{j}'
            jsondata[key] = [float(lat), float(lon), float(elev)]
            # TODO: Check we have i and j correct way around
            rows.append(f'{i},{j},{lat},{lon},{elev}' + NEWLINE)

    with open(f"{output_file_name}.csv", 'w') as outfile:
        outfile.write('x,y,lat,lon,elev' + NEWLINE)
        outfile.writelines(rows)
    with open(f"{output_file_name}.json", 'w') as outfile:
        json.dump(jsondata, outfile)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        input_file, output_file_name = args

        elevation_file = None
    elif len(args) == 3:
        input_file, output_file_name, elevation_file = args
    else:
        raise ValueError(
            'Invalid args. Should be input_file, <elevation_file>')

    generate_coordinate_file(
        input_file,
        output_file_name,
        elevation_file=elevation_file,
    )
