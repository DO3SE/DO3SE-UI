import logging

from do3se.util.jsondict import JsonDict
from do3se.util.csv2dict import csv2dict

class Config(JsonDict):
    """
    Extend JsonDict to implement application specific configuration methods
    """

    def __init__(self, filename, veg_csv=None):
        empty = {
            'file_history': list(),
            'input_format': dict(),
            'output_format': dict(),
            'site_params': dict(),
            'veg_params': dict(),
        }

        self.blacklist = {
                'input_format': list(),
                'output_format': list(),
                'site_params': list(),
                'veg_params': list(),
        }

        logging.info("Loading configuration file: " + filename)
        JsonDict.__init__(self, filename, empty)

        # Add supplied presets to stored presets
        if veg_csv:
            logging.debug('Loading extra presets: ' + veg_csv)
            veg_presets = csv2dict(open(veg_csv, 'r'))
            self.blacklist['veg_params'].extend(veg_presets.keys())
            self['veg_params'].update(veg_presets)



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
