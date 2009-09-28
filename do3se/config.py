import logging

from do3se.util.jsondict import JsonDict

class Config(JsonDict):
    """
    Extend JsonDict to implement application specific configuration methods
    """

    def __init__(self, filename):
        defaults = {
            'file_history': list(),
            'input_format': dict(),
            'output_format': dict(),
            'site_params': dict(),
            'veg_params': {
                'Coniferous Forests (CF)': {
                    'gmax': 160,
                    'fmin': 0.1,
                },
                'Deciduous Forests (DF)': {
                    'gmax': 134,
                    'fmin': 0.13,
                },
                'Needleleaf Forests (NF)': {
                    'gmax': 180,
                    'fmin': 0.13,
                },
                'Broadleaf Forests (BF)': {
                    'gmax': 200,
                    'fmin': 0.03,
                },
            },
        }

        logging.info("Loading configuration file: " + filename)
        JsonDict.__init__(self, filename, defaults)

        # TODO: Make this merge sets of params rather than only having
        #       defaults OR stored presets...


    def sync(self, *args, **kwargs):
        logging.debug("Saving configuration")
        JsonDict.sync(self, *args, **kwargs)


    def close(self, *args, **kwargs):
        logging.info("Closing configuration file")
        JsonDict.close(self, *args, **kwargs)


    def add_to_file_history(self, path):
        """
        Add a path to the file history

        The FileHistory object needs at most 9 paths.  This method adds a path
        to the file history list, and then trims it to the most recent 9 paths.
        """
        # Remove duplicates
        try:
            self['file_history'].remove(path)
        except ValueError:
            pass

        # Add path
        self['file_history'].append(path)
        # Trim to 9 lines
        self['file_history'] = self['file_history'][-9:]
        # Save the config
        self.sync()


    def sanitise(self):
        """
        Sanitise the configuration, removing references to fields that don't
        exists, etc.
        """
        import model
        # Remove references to non-existant input fields
        for key, preset in self['input_format'].iteritems():
            preset['fields'] = [x for x in preset['fields'] if x in model.input_field_map]
        # Remove references to non-existant output fields
        for key, preset in self['output_format'].iteritems():
            preset['fields'] = [x for x in preset['fields'] if x in model.output_field_map]
