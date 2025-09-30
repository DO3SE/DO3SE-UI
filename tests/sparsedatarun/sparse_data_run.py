from do3se.automate import run_from_pipe
from collections import namedtuple
import pandas as pd

import os

PROJECT_DIR = "tests/sparsedatarun"

os.makedirs(f"{PROJECT_DIR}/outputs", exist_ok=True)

output_fields=["afsty"]

options_raw = {
    "format": output_fields,
    "show_headers": True,
    "reduce_output": False,
}
input_fields = [
    "dd",
    "hr",
    "ts_c",
    "p",""
    "o3_ppb_zr",
    "precip",
    "Hd",
    "uh_zr",
    "r",
    "vpd",
]
output_fields = [
    "dd",
]

Options = namedtuple('Options', options_raw.keys())
options = Options(**options_raw)
project_file=f"{PROJECT_DIR}/configs/using_spanish_wheat_defaults_multiplicative_latlon.json"
outputfile = open(f"{PROJECT_DIR}/outputs/sparse_data_run_test_output.csv", 'w')
runner = run_from_pipe(
    options=options,
    projectfile=project_file,
    input_fields=input_fields,
    output_file=outputfile,
)

input_data = pd.read_csv(f"{PROJECT_DIR}/inputs/EXTRANWP_55_13.csv", names=input_fields, skiprows=1).to_dict(orient='records')
print(input_data[0])
runner(input_data=input_data)


# SPARSE RUN
outputfile = open(f"{PROJECT_DIR}/outputs/sparse_data_run_test_output_sparse.csv", 'w')

runner = run_from_pipe(
    options=options,
    projectfile=project_file,
    input_fields=input_fields,
    output_file=outputfile,
)

input_data = pd.read_csv(f"{PROJECT_DIR}/inputs/EXTRANWP_55_13_sparse.csv", names=input_fields, skiprows=1).to_dict(orient='records')
print(input_data[0])
runner(input_data=input_data)





# SPARSE RUN FILLED
outputfile = open(f"{PROJECT_DIR}/outputs/sparse_data_run_test_output_sparse_filled.csv", 'w')

runner = run_from_pipe(
    options=options,
    projectfile=project_file,
    input_fields=input_fields,
    output_file=outputfile,
)

input_data = pd.read_csv(f"{PROJECT_DIR}/inputs/EXTRANWP_55_13_sparse_filled.csv", names=input_fields, skiprows=1).to_dict(orient='records')
print(input_data[0])
runner(input_data=input_data)





# SPARSE RUN FILLED PLACEHOLDER
outputfile = open(f"{PROJECT_DIR}/outputs/sparse_data_run_test_output_sparse_filled_placeholder.csv", 'w')

runner = run_from_pipe(
    options=options,
    projectfile=project_file,
    input_fields=input_fields,
    output_file=outputfile,
)

input_data = pd.read_csv(f"{PROJECT_DIR}/inputs/EXTRANWP_55_13_sparse_filled_placeholder.csv", names=input_fields, skiprows=1).to_dict(orient='records')
print(input_data[0])
runner(input_data=input_data)

