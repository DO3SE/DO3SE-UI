"""This tool takes a directory of do3se outputs and maps the final POD values against the
latitude and longitude.
"""
import sys
import os
import json
import re


def get_headers(file):
    with open(file) as f:
        return f.readline().replace('\n', '').replace('\r\n', '').split(',')


def get_last_line_in_file(filename, headers):
    try:
        with open(filename, 'rb') as f:
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
            last_line = f.readline().decode().replace(
                '\n', '').replace('\r\n', '').replace('\r', '').split(',')
            last_line_data = {h: d for h, d in zip(headers, last_line)}
            return last_line_data
    except OSError:
        Warning(f'Os Error while getting last line in file {filename}')
        return {h: None for h in headers}


def get_last_line_of_files(dir, files, headers):
    last_lines = [get_last_line_in_file(dir + '/' + f, headers) for f in files]
    return last_lines


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def get_lat_long_from_file_name(file, coord_map):
    coords = list(filter(lambda x: is_int(
        x), re.split('[_-]|[.]', file)))
    coords_string = "_".join(coords)
    try:
        lat, long, elev = coord_map[coords_string]
        return lat, long, elev
    except KeyError:
        Warning(
            f"Filename invalid or {coords_string} not found in coord map file.")
        raise KeyError(
            f"Filename invalid or {coords_string} not found in coord map file.")


def get_coordinates(coordinate_file):
    with open(coordinate_file) as coordinate_file_data:
        coord_data = json.load(coordinate_file_data)
        return coord_data


def merge_data(line_data, lat_long_elev):
    # print(line_data.keys())
    lat, long, elev = lat_long_elev
    return [
        lat,
        long,
        elev,
        line_data['"PODY (mmol/m^2 PLA)"'],
        line_data['"POD0 (mmol/m^2 PLA)"'],
    ]
    # return {
    #     'lat': lat,
    #     'long': long,
    #     'pody': line_data['"PODY (mmol/m^2 PLA)"'],
    #     'pod0': line_data['"POD0 (mmol/m^2 PLA)"'],
    # }


def map_pody_to_geolocation(input_file_directory, coordinate_file, outfile):
    files = os.listdir(input_file_directory)
    headers = get_headers(input_file_directory + "/" + files[0])
    last_lines = get_last_line_of_files(input_file_directory, files, headers)
    coordinates = get_coordinates(coordinate_file)
    lat_long_elevs = [get_lat_long_from_file_name(
        f, coordinates) for f in files]
    final_data = [merge_data(line_data, lat_long_elev)
                  for line_data, lat_long_elev in zip(last_lines, lat_long_elevs)]
    # output_file = "pod_map.csv"
    # output_file = input_file_directory + "/" + "pod_map.csv"
    with open(outfile, 'w') as output_file_data:
        output_headers = 'lat,long, elev,pody,pod0'
        output_file_data.write(output_headers)
        output_file_data.write('\n')
        data_to_write = "\n".join([",".join([str(t) for t in line])
                                   for line in final_data])
        output_file_data.write(data_to_write)
        # json.dump(final_data, output_file_data)


if __name__ == "__main__":
    args = sys.argv[1:]
    input_file_directory, coordinate_file, outfile = args
    map_pody_to_geolocation(input_file_directory, coordinate_file, outfile)


# # %%
# def get_last_line_in_file(filename):
#     with open(filename, 'rb') as f:
#         f.seek(-2, os.SEEK_END)
#         while f.read(1) != b'\n':
#             f.seek(-2, os.SEEK_CUR)
#         last_line = f.readline().decode().split(',')
#         return last_line


# get_last_line_in_file(
#     './tests/multirun/outputs/using_spanish_wheat_defaults_multiplicative_latlon/input_2_3.csv')


# Multirun setup
# %%

# from tools.map_pody_to_geolocation import map_pody_to_geolocation
# import os
# PROJECT_DIR = "..."
# dirs = os.listdir(f'{PROJECT_DIR}/outputs')
# print(dirs)

# for d in dirs:
#     if d !="args.json":
#         print(d)
#         try:
#             map_pody_to_geolocation(f"{PROJECT_DIR}/outputs/{d}", '{PROJECT_DIR}/coordinates.json', f"../carbon_seq_runs/02/outputs_pod/{d}.csv")
#         except Exception:
#             print(f"Failed: {d}")
#             pass
