import sys
import os
import json
# import pandas as pd

if __name__ == "__main__":
    args = sys.argv[1:]
    coordinates_file_loc, = args
    with open(coordinates_file_loc) as coord_file_raw:
        lines = [line.split() for line in coord_file_raw]
        skip_rows = 1
        out_json = {f"{line[0]}_{line[1]}": [float(i) for i in line[2:4]]
                    for line in lines[skip_rows:]}
        out_file_loc = '.'.join(
            coordinates_file_loc.split('.')[0:-1]) + '.json'
        print(out_file_loc)
        with open(out_file_loc, 'w') as out_file:
            json.dump(out_json, out_file)

            # data = pd.read_table(coordinates_file_loc, skiprows=1,
            #                      delim_whitespace=True, names=['x', 'y', 'lat', 'long'])
            # data_json = data.iterrows()
            # print(data_json)
#
