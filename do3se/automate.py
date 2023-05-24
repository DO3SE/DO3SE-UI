from do3se.dataset import Dataset, data_from_csv
from do3se.project import Project
from do3se import model
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


def run(options, projectfile, inputfile, outputfile, parser, headings):
    project = Project(projectfile)
    if not project.exists():
        parser.error('Project file does not exist: ' + projectfile)

    # Extract parameters which control loading of data
    input_fields = project.data.pop('input_fields', [])
    input_trim = project.data.pop('input_trim', 0)
    input_data = data_from_csv(open(inputfile, 'r'), input_fields, input_trim)
    dataset = Dataset(input_data, input_fields, project.data, headings)
    # Run
    results = dataset.run()
    results.save(
        outputfile,
        options.format,
        options.show_headers,
        (project.data['sgs'], project.data['egs']) if options.reduce_output else None)


def run_from_pipe(options, projectfile, input_fields=[], output_file=None, headings=None):
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
        dataset = Dataset(input_data, input_fields, project.data, headings)
        results = dataset.run()
        if output_file:
            results.save(
                output_file,
                options.format,
                options.show_headers,
                (project.data['sgs'], project.data['egs']) if options.reduce_output else None)
        return results
    return _inner
