import click
import pandas as pd
from pathlib import Path
from do3se.gridrun import gridrun
from do3se.automate import list_outputs, format_option_callback, outfile_callback
from do3se import model
from do3se import application
# import wx
import sys
import optparse
import logging
_log = logging.getLogger('do3se.automate')


@click.group()
def cli():
    """Main cli entrypoint."""
    click.echo("Welcome to do3se_legacy_grid_run")


def get_option_parser():
    parser = optparse.OptionParser(
        usage='Usage: %prog [options] projectfile inputfile')
    parser.add_option('-v', '--verbose',
                      action='store_const',
                      dest='loglevel',
                      const=logging.INFO)
    parser.add_option('-d', '--debug',
                      action='store_const',
                      dest='loglevel',
                      const=logging.DEBUG)
    parser.add_option('--list-outputs',
                      action='callback',
                      callback=list_outputs,
                      #   callback_kwargs={'app': app}
                      )
    parser.add_option('-f', '--format',
                      action='callback',
                      callback=format_option_callback,
                      #   callback_kwargs={'app': app},
                      type='string',
                      nargs=1,
                      help='A comma-separated list of output field keys or +PRESET '
                           '(see --list-outputs) [default: all fields]')
    parser.add_option('-o', '--outfile',
                      action='callback',
                      callback=outfile_callback,
                      type='string',
                      nargs=1,
                      help='Write results to OUTFILE [default: use stdout]')
    parser.add_option('-r', '--reduce',
                      action='store_const',
                      dest='reduce_output',
                      const=True,
                      help='Only output rows during growing season')
    parser.add_option('-n', '--no-headers',
                      action='store_const',
                      dest='show_headers',
                      const=False,
                      help='Don\'t output column headers')
    parser.set_defaults(loglevel=logging.CRITICAL,
                        format=model.output_fields.keys(),
                        show_headers=True,
                        reduce_output=False,
                        outfile=sys.stdout)
    parser.add_option('-l', '--gridded-data',
                      action='store',
                      dest='gridded_data_map',
                      help='A json map of coordinate to lat long to parse configs')

    return parser

@click.argument('args', nargs=1)
@cli.command()
def main(args):
    # TODO: Check if this is ok or if args should be sys.argv[1:]
    parser = get_option_parser()
    (options, args) = parser.parse_args(args)
    if len(args) < 2:
        parser.error('Not enough arguments')
    application.logging_setup(level=options.loglevel)
    projectfile, inputfile = args
    outputfile = options.outfile
    run(options, projectfile, inputfile, outputfile, parser)


@click.option('-x', '--save_ds', default=False, help="If true saves a xr.dataset instead of csv's ")
@click.option('-v', '--debug', default=False, help="If true logs everything to the stdout")
@click.option('-b', '--target-batch-size', default=None, help="The target batch size for running sets of coordinates")
@click.argument(
    'coords_list',
    required=True,
    type=click.Path(),
)
@click.argument(
    'e_state_overrides_path',
    required=True,
    type=click.Path(),
)
@click.argument(
    'zero_year',
    required=True,
    type=int,
)
@click.argument(
    'output_location',
    required=True,
    type=click.Path(),
)
@click.argument(
    'input_data_dir',
    required=True,
    type=click.Path(),
)
@click.argument(
    'project_file',
    required=True,
    type=click.Path(),
)
@click.argument(
    'run-id',
    required=True,
    type=str,
)
@cli.command()
def run(run_id: str,
        project_file: Path,
        input_data_dir: Path,
        output_location: Path,
        zero_year: int,
        e_state_overrides_path: Path,
        coords_list: Path,
        target_batch_size: int = None,
        save_ds: bool = False,
        debug: bool = False,
        ):
    """Run the legacy DO3SE model on gridded data.

    Tested with EMEP and WRFchem outputs.

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
    coords_list : Path
        Path to file with list of coordinates to run the model on.
    target_batch_size : int
        The target batch size to run the model on. If None, the model will run on the full batch.
    save_ds : bool
        _description_
    debug : bool
        _description_
    """
    print("Running Legacy DO3SE from CLI. Input args:")
    print("run_id", run_id)
    print("project_file", project_file)
    print("input_data_dir", input_data_dir)
    print("output_location", output_location)
    print("zero_year", zero_year)
    print("e_state_overrides_path", e_state_overrides_path)
    print("coords_list", coords_list)
    print("target_batch_size", target_batch_size)
    print("save_ds", save_ds)
    print("debug", debug)
    # TODO: Calculate batches
    coords = pd.read_csv(coords_list).values
    gridrun(
        run_id,
        project_file,
        input_data_dir,
        output_location,
        zero_year,
        e_state_overrides_path,
        coords,
        save_ds=save_ds,
        debug=debug,
        target_batch_size=target_batch_size,
    )


if __name__ == "__main__":
    cli()
