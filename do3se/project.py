import logging
_log = logging.getLogger('do3se.project')

import wx

from util.picklefile import PickleFile
import dialogs


class Project(PickleFile):
    """
    Project file handler.

    :param filename:    Path to the project file if it currently exists
    :param window:      :class:`wx.Frame` the project belongs to (if using GUI)
    """
    def __init__(self, filename=None, window=None):
        PickleFile.__init__(self, filename)
        self.window = window

        if self.filename is not None:
            try:
                self.load()
            except EnvironmentError:
                self._error('Unable to load project ' + self.filename)
                self.data = dict()
            else:
                _log.info('Opened project ' + self.filename)
        else:
            _log.info('Created new project')
            self.data = dict()

    def _error(self, msg):
        """Log an error, but also notify the user if running a GUI."""
        _log.error(msg)
        if self.window is not None:
            wx.MessageBox(msg, 'Error', wx.OK|wx.ICON_ERROR, self.window)

    def save(self, save_as=False):
        """
        Save the project.

        :return:    True if project was saved, False otherwise
        """
        # If running in batch mode, no parent window for file dialogs
        if self.window is None:
            _log.error('Cannot save project in batch mode')
            return False

        # If we don't have a filename yet or are saving to a different file, get
        # a filename
        if self.filename is None:
            self.filename = dialogs.save_project(self.window)
        elif save_as:
            self.filename = dialogs.save_project(self.window, self.filename)

        # If we *still* don't have a filename, it's because the user changed
        # their mind
        if self.filename is None:
            return False

        # Attempt to save the file
        try:
            PickleFile.save(self)
        except EnvironmentError as e:
            self._error('Failed to save project %s (%s)' % (self.filename, str(e)))
            return False
        else:
            _log.info('Saved project ' + self.filename)
            return True
