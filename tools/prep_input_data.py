"""Prep the raw EMEP data for a DO3SE ui run.

- Adds headers
- Converts Units
- renames headers

NOTE: This is an example file and will need modifying to match data.

This should be ran after `convert_emep_netcdf_data` and `generate_coordinates_data_from_netcdf`.

After this has ran you can run the distributed cli.


"""
# %%

import click
from multiprocessing import Pool
from math import exp
import os
import pandas as pd

PROJECT_DIR = './2009'


def load_file(file):
    global PROJECT_DIR
    print(f"loading file: {file}")
    data = pd.read_csv(
        f"{PROJECT_DIR}/input_data_raw/{file}")
    # print(data.head())
    return data


def convert_hPa_to_kPa(data, pressure_fields='pressure'):
    """Convert pressure from hPa to kPa."""
    data['pressure_kpa'] = data[pressure_fields] / 10
    return data


def convert_tsk_to_tsc(data, temperature_field):
    """Convert temperature data from kelvin to degrees."""
    data['TsC'] = data[temperature_field] - 273.15
    return data


def add_hour_of_day(data):
    """Add hour per row."""
    row_count = len(data.index)
    if row_count % 24:
        raise ValueError("Row count must be a multiple of 24!")
    hours = [i for _ in range(int(row_count/24)) for i in range(24)]
    data['hr'] = hours
    return data


def add_julian_day(data):
    """Add julian day per row starting at 1."""
    row_count = len(data.index)
    if row_count % 24:
        raise ValueError("Row count must be a multiple of 24!")
    days = [i for i in range(1, int((row_count/24)+1)) for _ in range(24)]
    data['dd'] = days
    return data


def calculate_VPD(data, temp_field='TsC', rh_field='rh2m'):
    """Calculate VPD equation taken from pyDO3SE."""
    def saturated_vapour_pressure(Ts_C: float) -> float:
        return 0.611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
    esat = [saturated_vapour_pressure(t) for t in data[temp_field]]
    eact = (_esat * rh for _esat, rh in zip(esat, data[rh_field]))
    vpd = [es - ea for es, ea in zip(esat, eact)]
    data['VPD'] = vpd
    return data


def rename_fields(data, fields):
    for fin, fout in fields:
        data[fout] = data[fin]
    return data


def save_file(data, id):
    global PROJECT_DIR
    os.makedirs(f"{PROJECT_DIR}/inputs", exist_ok=True)
    data.to_csv(f"{PROJECT_DIR}/inputs/{id}", index=False)


def pick_fields(data):
    required_headings = ['dd', 'hr', 'TsC', 'pressure_kpa',
                         'o3_ppb_zr', 'Precip', 'Hd', 'uh_zr', 'VPD', 'CloudFrac']
    return data[required_headings]


# %%


def convert_file(filepath):
    """Get a pandas dataframe from the input data and pass it through the cleaning functions."""
    data = load_file(filepath)
    data = add_hour_of_day(data)
    data = add_julian_day(data)
    data = convert_tsk_to_tsc(data, 't2m')
    data = calculate_VPD(data)
    data = convert_hPa_to_kPa(data, 'Psurf')
    data = rename_fields(data, [('O3_45m', 'o3_ppb_zr'),
                                ('u_45m', 'uh_zr'), ('TsC', 'ts_c'), ('SH_Wm2', 'Hd')])
    data = pick_fields(data)
    save_file(data, filepath)
# %%


@click.group()
def cli():
    click.echo("Using prep input data tool")


@cli.command()
@click.argument("project_dir")
def run(
    project_dir,
):
    global PROJECT_DIR
    files_list = os.listdir(f'{project_dir}/input_data_raw')
    PROJECT_DIR = project_dir
    with Pool(processes=8) as pool:
        pool.map(convert_file, files_list)


if __name__ == "__main__":
    cli()
    # global PROJECT_DIR

# # %%
# # ======== TESTING ===========
# # %%
# filename = "EMEP_CELL_0_0.csv"
# data = load_file(filename)
# data = add_hour_of_day(data)
# data = add_julian_day(data)
# data = convert_tsk_to_tsc(data, 't2m')
# data = calculate_VPD(data)
# data = convert_hPa_to_kPa(data, 'Psurf')
# data = rename_fields(data, [('O3_45m', 'o3_ppb_zr'),
#                             ('u_45m', 'uh_zr'), ('TsC', 'ts_c'), ('SH_Wm2', 'Hd')])
# data = pick_fields(data)
# save_file(data, filename)
# data.head()
# # %%
# demo_data = pd.DataFrame([{'a': i} for i in range(120)])
# demo_data.head()
# # %%
# add_hour_of_day(demo_data)

# # %%
# demo_data_out = add_hour_of_day(demo_data)
# demo_data_out.head()

# # %%
# demo_data = pd.DataFrame([{'T2C': 10, 'rh2m_nwp': 0.21} for _ in range(120)])
# demo_data.head()

# # %%
# calculate_VPD(demo_data).head()

# # %%
# read_coords_file()

# # %%


# # %%
# [i for i in range(1, 10) for j in range(24)]
