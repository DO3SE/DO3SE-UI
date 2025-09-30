# %%
import xarray as xr
import numpy as np
# %%
dims = ['j', 'i']
input_data_example = xr.open_dataset('tests/gridrun/inputs/hourly_t2m_2012.nc')
overrides_ds = input_data_example.isel(time=0).squeeze().drop_vars('time')
overrides_ds
# %%
shape = overrides_ds[dims[0]].size, overrides_ds[dims[1]].size
shape
# %%
x = np.arange(shape[0])
y = np.arange(shape[1])
x.shape, y.shape, shape
# %%
overrides_ds = overrides_ds\
    .assign_coords(xb=(dims[0], x), yb=(dims[1], y)) \
    .rename_dims({dims[0]: 'x', dims[1]: 'y'}) \
    .drop(dims[0]).drop(dims[1]).rename({'xb': 'x', 'yb': 'y'})
overrides_ds
# %%
# REPLACE THIS WITH VARIABLES YOU WANT TO OVERRIDE
terrain = np.random.rand(*shape)
output_ds = overrides_ds.assign(terrain=(['x', 'y'], terrain))
output_ds = output_ds.drop('t2m')
output_ds
# %%
output_ds.to_netcdf('tests/gridrun/e_state_overrides.nc')

# %%
