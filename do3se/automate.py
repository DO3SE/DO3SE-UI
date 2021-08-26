from do3se.dataset import Dataset, data_from_csv
from do3se.project import Project
from do3se import model
from do3se import application
# import wx
import sys
import os
import optparse
import logging
_log = logging.getLogger('do3se.automate')


# class App(wx.App):
#     """Minimal wxPython application.

#     It's not possible to use :obj:`wx.StandardPaths` without first creating an
#     application instance.  This application class uses the same application
#     name as :class:`do3se.application.App` so that paths remain the same.
#     """

#     def OnInit(self):
#         self.SetAppName(application.app_name)
#         self.config = application.open_config()
#         return True


def list_outputs(option, opt_str, value, parser, app=None):
    """List available output formats and output fields and exit."""
    if app:
        print('Available output format presets')
        for p in app.config.data['output_formats'].keys():
            print('\t+' + p)

    print('Available output fields:')
    for f in model.output_fields.values():
        print('\t%(variable)-16s %(long)s' % f)

    exit(0)


def format_option_callback(option, opt_str, value, parser, app=None):
    """Parse format option, either as a list of fields or a preset name."""
    if len(value) == 0:
        parser.error('Invalid output format')

    if value[0] == '+' and app:
        preset = value[1:]
        if preset not in app.config.data['output_formats']:
            parser.error('Output format preset doesn\'t exist: ' +
                         preset + ' (see --list-outputs)')
        parser.values.format = app.config.data['output_formats'][preset]['fields']
        parser.values.show_headers = app.config.data['output_formats'][preset]['headers']
        parser.values.reduce_output = app.config.data['output_formats'][preset]['reduce']
    else:
        parser.values.format = value.split(',')
        for f in parser.values.format:
            if f not in model.output_fields:
                parser.error('Output field doesn\'t exist: ' +
                             f + ' (see --list-outputs)')


def outfile_callback(option, opt_str, value, parser):
    """Open a different output file."""
    parser.values.outfile = open(value, 'w')


def run(options, projectfile, inputfile, outputfile, parser):
    project = Project(projectfile)
    if not project.exists():
        parser.error('Project file does not exist: ' + projectfile)

    # Extract parameters which control loading of data
    input_fields = project.data.pop('input_fields', [])
    input_trim = project.data.pop('input_trim', 0)
    input_data = data_from_csv(open(inputfile, 'r'), input_fields, input_trim)
    dataset = Dataset(input_data, input_fields, project.data)
    # Run
    results = dataset.run()
    results.save(
        outputfile,
        options.format,
        options.show_headers,
        (project.data['sgs'], project.data['egs']) if options.reduce_output else None)


def run_from_pipe(options, projectfile, input_fields=[], output_file=None):
    """Run model with piped data.

    input_data must be iterable of dicts

    Example
    -------
    runner = run_from_pipe(options, projectfile, output_file, parser)
    output = runner(input_data)
    """
    def _inner(input_data, project_overrides={}):
        project = Project(projectfile)
        project.data = {**project.data, **project_overrides}
        dataset = Dataset(input_data, input_fields, project.data)
        results = dataset.run()
        if output_file:
            results.save(
                output_file,
                options.format,
                options.show_headers,
                (project.data['sgs'], project.data['egs']) if options.reduce_output else None)
        return results
    return _inner


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


def main(args):
    parser = get_option_parser()
    (options, args) = parser.parse_args(args)
    if len(args) < 2:
        parser.error('Not enough arguments')
    application.logging_setup(level=options.loglevel)
    projectfile, inputfile = args
    outputfile = options.outfile
    run(options, projectfile, inputfile, outputfile, parser)


if __name__ == '__main__':
    main(sys.argv[1:])
