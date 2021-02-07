"""This cli entrypoint is for running distributed multiruns.

Example run:
`python DO3SE_cli_distributed.py --config-format='json' --gridded-data='tests/multirun/coordinates.json' ./tests/multirun`
"""

import sys
import os
import re
import json
from multiprocessing import Process
from do3se.automate import run, main, get_option_parser


def make_dir(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def get_lat_long(input_file_name, coordinate_map_file):
    coords = list(filter(lambda x: is_int(
        x), re.split('[_-]|[.]', input_file_name)))
    with open(coordinate_map_file) as coordinate_map_file_raw:
        coord_map = json.load(coordinate_map_file_raw)
        coords_string = "_".join(coords)
        try:
            lat, long = coord_map[coords_string]
            return ([lat, long], coords)
        except KeyError:
            Warning(
                f"Filename invalid or {coords_string} not found in coord map file.")
            raise KeyError(
                f"Filename invalid or {coords_string} not found in coord map file.")


def inject_location_into_config(config_dir: str, config_file: str, coordinate_map_file: str, input_file: str, target_config_dir: str):
    """Extract the coordinates from the filename and get the lat long from a coordinate map.

    Filename should represent `name_{x_coord}_{y_coord}` for example `datainput_2_4.csv`
    Coordinate_map_file should be a json that maps `{ "<x_coord>_<y_coord>": [<lat>,<long>] }`
        for example: `{"2_4": [27.3,-4.28], "2_5": [28.9, -5.23]}`
    """
    [lat, long], [x, y] = get_lat_long(input_file, coordinate_map_file)
    with open(f"{config_dir}/{config_file}") as config_file_raw:
        config_data = json.load(config_file_raw)
        config_data['lat'] = lat
        config_data['lon'] = long
        new_config_file_name = f"{target_config_dir}/{config_file.split('.')[0]}_{x}_{y}.json"
        make_dir(target_config_dir)
        with open(new_config_file_name, 'w') as new_config_file_raw:
            json.dump(config_data, new_config_file_raw)
        return new_config_file_name


def run_file(config_file, input_file, output_file, options):
    # TODO: Need to allow a per input file alteration
    print(f"Running config: {config_file} on input: {input_file}")
    args_in = options + \
        [f'--outfile={output_file}'] + [config_file, input_file]
    p = Process(target=main, args=(args_in, ))
    # p = Process(target=main, args=(config_file, input_file, ))
    p.start()
    return p


def get_file_directories_and_options(parser, parsed_args, args):
    """ Get Config, input and output Directories."""

    if len(parsed_args) == 1:
        project_dir, = parsed_args
        config_dir = f"{project_dir}/configs"
        input_dir = f"{project_dir}/inputs"
        output_dir = f"{project_dir}/outputs"
        options = args[:-1]
    elif len(parsed_args) == 3:
        options = args[:-3]
        config_dir, input_dir, output_dir = parsed_args
    else:
        options = None
        config_dir = None
        input_dir = None
        output_dir = None
        parser.error(
            "Args must be <project_dir> or <config_dir> <input_dir> <output_dir>")
    return config_dir, input_dir, output_dir, options


def run_distributed(config_files, input_files, config_dir, input_dir, output_dir,  options, gridded_data_map=None):
    processes_running = []
    failed_runs = []
    for config_file in config_files:
        output_dir_full = output_dir + '/' + config_file.split('.')[0]
        config_loc = config_dir + '/' + config_file
        make_dir(output_dir_full)
        for input_file in input_files:
            try:
                config_loc_injected = inject_location_into_config(
                    config_dir, config_file, gridded_data_map, input_file, config_dir + '/location'
                ) if gridded_data_map else config_loc
                processes_running.append(
                    run_file(
                        config_file=config_loc_injected,
                        input_file=input_dir + '/' + input_file,
                        output_file=output_dir_full + '/' + input_file,
                        options=options,
                    )
                )
            except:
                failed_runs.append(f"{config_file}-{input_file}")
    if len(failed_runs):
        print("Some runs failed:")
        print(failed_runs)


if __name__ == "__main__":
    args = sys.argv[1:]

    parser = get_option_parser()
    # print(options)
    parser.set_usage('Usage: %prog [options] config_dir input_dir output_dir')

    (parsed_options, parsed_args) = parser.parse_args(args)
    config_dir, input_dir, output_dir, options = get_file_directories_and_options(
        parser, parsed_args, args)

    print(config_dir)
    print(input_dir)
    print(output_dir)

    config_file_type = parsed_options.config_format or 'do3se'
    config_files = [c for c in os.listdir(config_dir) if len(c.split('.')) == 2 and c.split('.')[
        1] == config_file_type]
    print(config_files)
    print(config_file_type)
    input_files = os.listdir(input_dir)
    run_distributed(config_files, input_files, config_dir, input_dir, output_dir, options,
                    parsed_options.gridded_data_map)
