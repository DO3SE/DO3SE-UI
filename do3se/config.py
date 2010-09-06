import logging
_log = logging.getLogger('do3se.config')

from util.picklefile import PickleFile
from util import OrderedDict

class Config(PickleFile):
    """Application configuration file handler.

    Extends :class:`PickleFile` to implement application configuration logic,
    such as ensuring certain configuration keys always exist.
    """
    def __init__(self, filename):
        PickleFile.__init__(self, filename)
        
        # Load file if it exists
        if self.exists():
            self.load()
            _log.info('Loaded configuration file ' + self.filename)
        else:
            self.data = dict()
            _log.info('Creating new configuration file ' + self.filename)

        # Make sure required items exist
        if not 'presets' in self.data:
            self.data['presets'] = OrderedDict()
        if not 'recent_projects' in self.data:
            self.data['recent_projects'] = list()
        if not 'recent_files' in self.data:
            self.data['recent_files'] = list()

    def add_recent_project(self, path):
        """Add a path to the recent project list.
        
        This keeps a list of no more than the 9 most recently loaded/saved
        projects.  The limit of 9 entries mirrors that of the
        :class:`wx.FileHistory` class.
        """
        # Remove duplicates
        try:
            self.data['recent_projects'].remove(path)
        except ValueError:
            pass
        # Add path
        self.data['recent_projects'].append(path)
        # Trim to most recent 9
        self.data['recent_projects'] = self.data['recent_projects'][-9:]

    def add_recent_file(self, path):
        """Add a path to the recent data file list.

        Maintains a lits of no more than the 9 most recently run data fies
        in ``data['recent_files']``.  The limit mirrors that of the
        :class:`wx.FileHistory` class.
        """
        # Remove duplicates
        try:
            self.data['recent_files'].remove(path)
        except ValueError:
            pass
        # Add path
        self.data['recent_files'].append(path)
        # Trim to most recent 9
        self.data['recent_files'] = self.data['recent_files'][-9:]
