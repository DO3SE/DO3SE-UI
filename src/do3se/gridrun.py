import sys
import os
import math
import numpy as np
import pandas as pd
import xarray as xr
from warnings import warn
from collections import namedtuple
from typing import Tuple, Callable, List, Union, Dict
from datetime import datetime
from pathlib import Path

from do3se.automate import run_from_pipe
from do3se.logger import Logger
from do3se.version import app_version

INVALID_COORD = -9999

def saturated_vapour_pressure(Ts_C: float) -> float:
    return 0.611 * math.exp(17.27 * Ts_C / (Ts_C + 237.3))


def calculate_VPD(Ts_C, rh):
    """Calculate VPD equation taken from pyDO3SE."""
    esat = saturated_vapour_pressure(Ts_C)
    eact = esat * rh
    vpd = esat - eact
    return vpd


def add_vpd(x):
    def _inner(ts_c, rh):
        # TODO: Incorrect args passed to calculate vpd
        return np.apply_along_axis(lambda d: calculate_VPD(*d), 0, [ts_c, rh])
    return xr.apply_ufunc(_inner, x.ts_c, x.rh, dask="parallelized",
                          output_dtypes=np.float64)


def load_estate_overrides(
    e_state_overrides_path: Path,
):
    e_state_override_data = xr.open_dataset(e_state_overrides_path)
    assert e_state_override_data.x, "x not found in e_state_override_data"
    assert e_state_override_data.y, "y not found in e_state_override_data"
    # # TODO: e_state_override file should contain x and y coords
    # grid_size = e_state_override_data.terrain[0].size
    # grid_shape = e_state_override_data.terrain[0].shape
    # dims = ['j', 'i'] # TODO: Assert i and j are in estate_override_data dims
    # y = np.arange(grid_size).reshape(grid_shape) % grid_shape[1]
    # x = (np.arange(grid_size).reshape(list(reversed(grid_shape))) %
    #      grid_shape[0]).transpose()
    # dscoords = dict(
    #     i=e_state_override_data.i,
    #     j=e_state_override_data.j,
    # )
    # x_da = xr.DataArray(x, dscoords,
    #                     dims=dims)
    # y_da = xr.DataArray(y, dscoords,
    #                     dims=dims)
    # e_state_override_data = e_state_override_data.assign_coords(
    #     dict(x=x_da, y=y_da))
    return e_state_override_data


def process_wrfchem_data(data_processed, dims=['lon', 'lat']):
    data_processed = data_processed.assign(hr=lambda d: d.XTIME.dt.hour)
    data_processed = data_processed.assign(
        dd=lambda d: d.time.dt.strftime('%j').astype(int))
    data_processed = data_processed.assign(ts_c=lambda d: d.T2 - 273.15)
    data_processed = data_processed.assign(hd=lambda d: -d.HFX)
    data_processed = data_processed.assign(p=lambda d: d.PSFC / 1000)
    data_processed = data_processed.assign(rh=lambda d: d.RH2/100)
    data_processed = data_processed.assign(par=lambda d: d.SWDDIR + d.SWDDIF)
    data_processed = data_processed.assign(vpd=add_vpd) # Calculates VPD from ts_c and rh

    data_processed = data_processed.rename_vars(
        # Modify this if changing input headings
        # Keys are headings in input data and values are the names of the variables in the model
        **dict([
            ('o3', 'o3_ppb_zr'),
            ('WINDSPEED10', 'uh_zr'),
            # ('Ts_C', 'ts_c'),
            # ('SH_Wm2', 'hd'),
            ('PRECIP', 'precip'),
            ('UST', 'ustar_ref'),
            ('SMOIS', 'asw'),  # TODO: INPUT Sn?
        ])
    )

    data_processed_indexed = data_processed.squeeze()
    grid_size = data_processed_indexed.ts_c[0].size
    grid_shape = data_processed_indexed.ts_c[0].shape

    # TODO: This may be specific to dataset.
    # TODO: This is braking with EMEP data
    y = np.arange(grid_size).reshape(grid_shape) % grid_shape[1]
    x = (np.arange(grid_size).reshape(list(reversed(grid_shape))) %
         grid_shape[0]).transpose()
    x_da = xr.DataArray(x.transpose(), data_processed_indexed.coords,
                        dims=dims)
    y_da = xr.DataArray(y.transpose(), data_processed_indexed.coords,
                        dims=dims)
    data_processed_indexed = data_processed_indexed.assign_coords(
        dict(x=x_da, y=y_da))


    return data_processed_indexed


def process_emep_data(data_processed, dims=['j', 'i']):
    data_processed = data_processed.assign(hr=lambda d: d.time.dt.hour)
    data_processed = data_processed.assign(
        dd=lambda d: d.time.dt.strftime('%j').astype(int))
    data_processed = data_processed.assign(ts_c=lambda d: d.t2m - 273.15)
    data_processed = data_processed.assign(hd=lambda d: -d.SH_Wm2)
    data_processed = data_processed.assign(rh=lambda d: d.rh2m/100)
    data_processed = data_processed.assign(p=lambda d: d.Psurf / 10)
    data_processed = data_processed.assign(vpd=add_vpd) # Calculates VPD from ts_c and rh
    data_processed = data_processed.rename_vars(
        # Modify this if changing input headings
        # Keys are headings in input data and values are the names of the variables in the model
        **dict([
            ('O3_45m', 'o3_ppb_zr'),
            ('u_45m', 'uh_zr'),
            ('ts_c', 'ts_c'),
            # ('SH_Wm2', 'hd'),
            ('Precip', 'precip'),
            ('CloudFrac', 'cloudfrac'),
            ('met2d_ustar_nwp', 'ustar_ref'),
            # ('ustar_nwp', 'ustar_ref'),
            ('SMI_deep', 'asw'),
        ])
    )

    data_processed_indexed = data_processed.squeeze()
    # TODO: Check if this is needed for EMEP data
    grid_size = data_processed_indexed.ts_c[0].size
    grid_shape = data_processed_indexed.ts_c[0].shape

    y = np.arange(grid_size).reshape(grid_shape) % grid_shape[1]
    x = (np.arange(grid_size).reshape(list(reversed(grid_shape))) %
            grid_shape[0]).transpose()
    dscoords = dict(
        i=data_processed_indexed.i,
        j=data_processed_indexed.j,
    )
    x_da = xr.DataArray(x, dscoords,
                        dims=dims)
    y_da = xr.DataArray(y, dscoords,
                        dims=dims)
    data_processed_indexed = data_processed_indexed.assign_coords(
        dict(x=x_da, y=y_da))

    return data_processed_indexed


def load_and_process(
        data_location, process_func=process_emep_data,
        dims=['lat', 'lon'], **kwargs):
    try:
        input_data_multi_ds = xr.open_mfdataset(
            f'{data_location}/*.nc',
            # NOTE: Chunks can be overriden by kwargs
            **{"chunks":{'time': 8760, 'i': 5, 'j': 5},**kwargs},
            # , concat_dim="Time", combine="nested"
        )
    except OSError as e:
        print(f"No files found in {data_location}")
        print("Files in data dir: ", os.listdir(data_location))
        raise e
    except ValueError as e:
        print(f"Error opening files in {data_location}")
        print(os.listdir(data_location))
        print(kwargs)
        raise e
    # TODO: Filter for batch
    #  .where(lambda d: (d.i.isin(x)) & (d.j.isin(y)), drop=True)
    # TODO: Chunks .chunk({'i': 5, 'j': 5, 'time': 8760})

    data_processed = process_func(input_data_multi_ds, dims=dims)

    return data_processed

def get_coord_batches(
    coords, target_batch_size=1000, logger=print,
    data_computed=None):
    """Get batches of coordinates for parallel processing.

    Returns
    -------
    list
        List of tuples of (x, y) coordinates
    """

    if coords == "all":
        if data_computed is None:
            raise ValueError("data_computed must be provided if coords is 'all'")
        coords = np.array(list(zip(data_computed.x.values.flatten(),data_computed.y.values.flatten())))

    batch_len = math.ceil(len(coords)/target_batch_size)
    batch_size = math.ceil(len(coords) / batch_len)
    logger(f"===total cells: {len(coords)} batch_size: {batch_size}, batch_len:{batch_len}, target_batch_size={target_batch_size}")
    pad_amount = (batch_len*batch_size) - coords.shape[0]

    coords_batches = np.pad(coords,  [[0,pad_amount],[0,0]], 'constant', constant_values=INVALID_COORD).reshape([batch_len, batch_size, 2])
    return coords_batches


out_fields = [
    'dd', 'hr',
    'ts_c', 'p', 'o3_ppb_zr', 'precip', 'hd', 'uh_zr', 'vpd', 'cloudfrac',
    'ustar_ref',
    'asw',
    'gsto_l', 'afsty', 'fst_sun', 'aot40',
    'lai', 'fvpd', 'parsun', 'parshade', 'fxwp', 'o3_ppb', 'ustar',
]


def get_config_overrides_from_estate(
    location_data: xr.Dataset,
    e_state_overrides_fields: Dict[str, str],
) -> Dict[str, any]:
    """Get config overrides from estate overrides file.

    Parameters
    ----------
    location_data : xr.Dataset
        Dataset containing estate overrides
    e_state_overrides_fields : Dict[str, str]
        Mapping of estate overrides fields to config overrides

    Returns
    -------
    Dict[str, any]
        Dictionary of config overrides
    """
    config_overrides = {}
    for estate_field, config_field in e_state_overrides_fields.items():
        if estate_field in location_data:
            config_overrides[config_field] = float(location_data[estate_field].values[0])
        else:
            warn(f"Warning: {estate_field} not found in estate overrides file")
    return config_overrides

def process_output_for_pod(results):
    """Add variables to outputs."""
    return {
        "pody": results.data[-1]['afsty'],
        "aot40": results.data[-1]['aot40'],
    }

def process_and_run(
    data_location: Path,
    e_state_overrides_path: Path,
):
    """Create a runner function for the DO3SE model.

    Parameters
    ----------
    data_location : Path
        Location of netcdf files
    e_state_overrides_path : Path
        Location of estate overrides file


    To aid in runnng the functions over multiple files and grid cells this function outputs
    nested functions.

    process_and_run -> _data_prep -> _runner

    process_and_run
    ---------------
    This function takes the data locations and setup parameters

    _data_prep
    ----------
    This function takes a list of coordidates to load and process the data for
    all these coordinates.


    _runner
    -------
    This function takes the data and runs the DO3SE model for each grid cell.]
    The runner can be given different config files or output requirements.
    This means the same data can be ran for multiple cultivars.

    """
    def _data_prep(
            coords: List[Tuple[int, int]],
            preprocess_data_func=process_emep_data,
            return_processed_data=False, precompute=False,
            dims: List[str] = ['lon', 'lat'],
            loadData_kwargs: dict = {},
            logger=print
        ):
        """Load and process data for coords in coords list.

        Parameters
        ----------
        coords : List[Tuple[int, int]] or "all"
            _description_
        log_level : int, optional
            _description_, by default 0
        preprocess_data_func : _type_, optional
            _description_, by default lambdax:x
        target_batch_size : int, optional
            target coord batch size for each run, by default 100
        return_processed_data : bool, optional
            _description_, by default False
        precompute : bool, optional
            _description_, by default False
        save_ds : bool, optional
            If true will combine all outputs to a netcdf file
            If false will save each output as a csv file, by default False
        dims : List[str], optional
            Dimensions to use for the data, by default ['lon', 'lat']
            This should match the dimensions in the netcdf files
        logger: print
            _description_, by default print

        """
        logger("loading data")
        start_time = datetime.now()
        data = load_and_process(
            data_location,
            process_func=preprocess_data_func,
            dims=dims,
            **loadData_kwargs,
            # concat_dim="Time", # TODO: Make this an arg
            # combine="nested", # TODO: Make this an arg
        )
        logger("data shape", data.ts_c.shape)
        # x, y = list(zip(*coords))
        e_state_overrides = load_estate_overrides(
            e_state_overrides_path,
            # grid_size, grid_shape, x, y, dims
            )
        logger("Computing data")
        # coord_map = get_coord_map(mask_path)

        if return_processed_data:
            return data
        # TODO: Filter data by coords
        data_computed = data if not precompute \
            else data.compute()
        # TODO: Get chunks
        # TODO: Check why we saved here!
        # data_computed.to_netcdf(tmp_data_loc)
        # data_computed.chunk({'time': 10}).to_netcdf(tmp_data_loc)
        # data_computed = xr.open_dataset(tmp_data_loc)


        end_time = datetime.now()
        logger(f"Pre process time: {end_time - start_time}")

        return data_computed, e_state_overrides
    return _data_prep

def runner(
    project_file_path: Path,
    coords: List[Tuple[int, int]],
    data_computed: xr.Dataset,
    output_fields: List[str],
    e_state_overrides: xr.Dataset,
    zero_year: int,
    e_state_overrides_field_map: Dict[str, str] = None,
    output_file_path: Path=None,
    process_output: Callable[[], any] = process_output_for_pod,
    throw_exceptions: bool = True,
    run_id="DO3SE_UI_run",
    save_ds: bool = False,
    logger=Logger(0),
):
    """Run the do3se model for the given project file.

    Parameters
    ----------
    project_file_path : Path
        path to project file
    coords: List[Tuple[int, int]]
        List of coordinates to run the model for
    data_computed : xr.Dataset
        met data to run the model for
    e_state_overrides : xr.Dataset
        estate overrides data
    zero_year : int
        Set to be the year of the first day of the simulation.
    e_state_overrides_field_map: Dict[str, str], optional
        A mapping of e_state_override.nc fields to project file fields
    output_fields : List[str]
        _description_
    output_file_path : _type_
        _description_
    process_output : Callable[[], any], optional
        Function to process outputs from the DO3SE model, by default None
    throw_exceptions: bool = False,
        If true will throw exceptions if the model fails to run
        If false failing coords will be skipped
    run_id : str, optional
        _description_, by default "DO3SE_UI_run"
    save_ds : bool, optional
        If true will combine all outputs to a netcdf file
    batch_i : int, optional
        batch index, by default 0

    Returns
    -------
    _type_
        _description_
    """
    outputs = []
    outputs_full = []
    start_time = datetime.now()
    logger(f"Running model for {len(coords)} coords")
    for x, y in coords:
        if x == INVALID_COORD and y == INVALID_COORD:
            continue
        logger(f'Running coords: {x}_{y}')
        try:
            # TODO: Can we optimize this?!
            # rows = data_computed.where(
            #     lambda d: (d.x == i) & (d.y == j), drop=True).to_dataframe(
            # ).to_dict('records')
            #                 # TODO: Can we optimize this?!
            rows_df = data_computed.where(
                lambda d: (d.x == x) & (d.y == y), drop=True).to_dataframe(
            )
            rows = rows_df.values
            location_data = e_state_overrides.where(
                lambda d: (d.x == x) & (d.y == y), drop=True)

            elevation = location_data.terrain.values[0, 0].tolist()[0]
            lat = location_data.lat.values[0].tolist()[0]
            lon = location_data.lon.values[0].tolist()[0]
            input_data_lat = rows_df.lat.iloc[0]
            input_data_lon = rows_df.lon.iloc[0]
            grid_i = rows_df.reset_index().i.values[0].tolist()
            grid_j = rows_df.reset_index().j.values[0].tolist()

            logger(f"Running coords: {x}_{y} with elevation: {elevation}, lat: {lat}, lon: {lon}, grid_i: {grid_i}, grid_j: {grid_j}")
            assert lat == input_data_lat, f"input_data and e_state_overrides lat do not match, {lat} != {input_data_lat}"
            assert lon == input_data_lon, f"input_data and e_state_overrides lon do not match, {lon} != {input_data_lon}"

            additional_e_state_overrides = get_config_overrides_from_estate(
                location_data,
                e_state_overrides_field_map,
            ) if e_state_overrides_field_map is not None else {}
            logger("using the following additional config overrides from e_state_overrides.nc", additional_e_state_overrides)

            input_fields = list(rows_df.columns)
            config_overrides = {
                "input_fields": input_fields,
                "elev": elevation,
                "lat": float(lat),
                "lon": float(lon),
                **additional_e_state_overrides,
            }

            options_raw = {
                "format": output_fields,
                "show_headers": True,
                "reduce_output": False,
            }
            Options = namedtuple('Options', options_raw.keys())
            options = Options(**options_raw)

            # If save_ds is false then we save each run to a separate csv file
            output_file = open(
                f'{output_file_path}/{run_id}_{x}_{y}.csv', 'w') \
                if output_file_path is not None and not save_ds else None
            logger("Running do3se on coords: ", x, y)

            runner_int = run_from_pipe(
                options,
                project_file_path,
                input_fields,
                output_file=output_file,
                headings=input_fields,
            )

            output = runner_int(rows, config_overrides)
            if output_file:
                logger("Runner output saved to", output_file_path, "for coords", x, y)

            if save_ds:
                logger("Saving ds output for coords", x, y)
                # TODO: Can we skip dataframe here?
                df = pd.DataFrame(output.data)
                df['x'] = x
                df['y'] = y
                df['i'] = x + 1 # retained for backwards compatibility
                df['j'] = y + 1 # retained for backwards compatibility
                df['grid_i'] = grid_i
                df['grid_j'] = grid_j
                df['lat'] = float(lat)
                df['lon'] = float(lon)
                zero_date = pd.to_datetime(f'{zero_year}-01-01')
                df['date'] = zero_date + \
                    pd.to_timedelta(df.dd, unit='D') + \
                    pd.to_timedelta(df.hr, unit='h')
                df = df.set_index(['x', 'y', 'date'])
                ds = df.to_xarray()
                outputs_full.append(ds)

            if process_output:
                logger("Processing output for coords", x, y)
                output_processed = process_output(output)
                outputs.append({
                    **output_processed,
                    "lat": lat,
                    "lon": lon,
                    "elev": elevation,
                    "x": x,
                    "y": y,
                    "grid_i": grid_i,
                    "grid_j": grid_j,
                })
        except Exception as e:
            if throw_exceptions:
                raise e
            else:
                logger(e)
                logger(f'Failed to run coords: {x}_{y}')
        output_file and output_file.close()
    end_time = datetime.now()
    logger(f"Completed running batch. Model time: {end_time - start_time}")
    if save_ds:
        logger("Saving full ds output")
        ds_full = xr.merge(outputs_full)
        ds_full.to_netcdf(f'{output_file_path}/out_full_{run_id}.nc')

    return outputs

def gridrun(
    run_id: str,
    project_file: Path,
    input_data_dir: Path,
    output_location: Path,
    zero_year: int,
    e_state_overrides_path: Path,
    coords: Union[str,List[Tuple[int, int]]],
    e_state_overrides_field_map: Dict[str, str] = None,
    preprocess_data_func: Callable[[xr.Dataset], xr.Dataset] = process_emep_data,
    process_output: Callable[[], any] = process_output_for_pod,
    dims: Tuple[str, str]=['j', 'i'],
    return_outputs: bool = False,
    output_fields: List[str] = out_fields,
    save_ds: bool = False,
    save_full_outputs: bool = False,
    target_batch_size: int = None,
    loadData_kwargs: dict = {},
    debug: bool = False,
):
    """Internal do3se run function

    Parameters
    ----------
    run_id : str
        A user assigned run id which can be used to identify each run.
    project_file : Path
        the path to the do3se project file(Config file)
    input_data_dir : Path
        Path to input data directory. This should contain the wrfchem output files.
    output_location : Path
        The path to the output directory.
    zero_year : int
        Set to be the year of the first day of the simulation.
    e_state_overrides_path : Path
        Path to the e_state_overrides.nc file.
    coords : List[Tuple[int, int]]
        list  of coordinates to run the model on
    e_state_overrides_field_map : Dict[str, str], optional
        A dictionary mapping the e_state_overrides field names to the input data field names, by default None
    preprocess_data_func : Callable[[xr.Dataset], xr.Dataset], optional
        A function to preprocess the input data before running the model, by default process_emep_data
    process_output : Callable[[], any]
        A function to process the output of the model before concatenating it.
    dims : List[str]
        The dimensions used in the input data
    return_outputs : bool
        If true, return the output of the model. Note this will use more memory
    output_fields: List[str]
        The fields to output from the model. Run list_outputs to see options
    save_ds : bool
        If true, save the full output dataset to a netcdf file.
    save_full_outputs : bool
        If true, save the full output from each run to csv files
    target_batch_size : int
        The target batch size to run the model on. If None, the model will run on the full batch.
    loadData_kwargs : dict
        kwargs to pass to the loadData function
    debug : bool
        Run in debug mode

    Returns
    -------
    _type_
        _description_
    """
    # SETUP MODEL

    logger=Logger(
        debug and 2,
        log_to_file=f'{output_location}/log_{run_id}.txt'if not debug else None,
        flush_per_log=debug,
        use_timestamp=True,
    )
    logger(f"Running grid run: {run_id}. With model version {app_version}")
    outputs = []
    setup = process_and_run(
        input_data_dir,
        e_state_overrides_path,
    )
    if save_ds and not save_full_outputs:
        raise ValueError(
            "save_ds cannot be True if save_full_outputs is False")


    full_output_dir = \
        f'{output_location}/full_outputs'\
        if save_full_outputs else None

    if full_output_dir:
        os.makedirs(full_output_dir, exist_ok=True)

    coordinate_batches = get_coord_batches(
        coords, target_batch_size=target_batch_size, logger=logger)


    for batch_i, coord_batch in enumerate(coordinate_batches):
        logger(f"===batch_i: {batch_i}")

        data_computed, e_state_overrides = setup(
            coords=coord_batch,
            dims=dims,
            preprocess_data_func=preprocess_data_func,
            precompute=loadData_kwargs.pop('precompute', False),
            loadData_kwargs=loadData_kwargs,
            logger=logger,
        )

        out_i = runner(
            project_file,
            coord_batch,
            data_computed,
            output_fields,
            e_state_overrides,
            zero_year,
            output_file_path=full_output_dir,
            e_state_overrides_field_map=e_state_overrides_field_map,
            process_output=process_output,
            run_id=run_id,
            save_ds=save_ds,
            logger=logger,
        )
        df = pd.DataFrame(out_i)
        if return_outputs:
            outputs.append(out_i)
        else:
            file_save_path = f'{output_location}/results_{batch_i}.csv'
            df.to_csv(file_save_path, index=False)

    return outputs