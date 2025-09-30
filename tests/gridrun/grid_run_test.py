# %%
# deprecated test
from do3se.gridrun import gridrun
import pandas as pd
import numpy as np
PROJECT_DIR = "tests/gridrun"
coords_list= f"{PROJECT_DIR}/coords.csv"
coords = pd.read_csv(coords_list).values

def process_output(results):
    """Add variables to outputs."""
    return {
        "pody": results.data[-1]['afsty'],
        "aot40": results.data[-1]['aot40'],
    }
out = gridrun(
        run_id=1,
        project_file=f"{PROJECT_DIR}/configs/Temperate_oak.json",
        input_data_dir=f"{PROJECT_DIR}/inputs",
        output_location=f"{PROJECT_DIR}/outputs",
        zero_year=2012,
        e_state_overrides_path=f"{PROJECT_DIR}/e_state_overrides.nc",
        # e_state_overrides_field_map=e_state_overrides_field_map,
        coords=coords,
        save_ds=True,
        save_full_outputs=True,
        debug=True,
        target_batch_size=2,
        dims=['j', 'i'],
        output_dims=['foo', 'bar'],
        process_output=process_output,
        loadData_kwargs=dict(
            precompute=True,
            chunks={'time': 8760, 'i': 1, 'j': 1},
        ),
)
out
# %%