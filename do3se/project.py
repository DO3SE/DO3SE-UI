import logging
import shutil
try:
    import cPickle as pickle
except ImportError:
    import pickle

import wx

import dialogs


class Project:
    """
    Project file handler.

    :param filename:    Path to the project file if it currently exists
    :param window:      :class:`wx.Frame` the project belongs to (if using GUI)
    """
    log = logging.getLogger('do3se.project')

    def __init__(self, filename=None, window=None):
        self.filename = filename
        self.window = window

        # Load the file if this isn't a new project
        if self.filename is not None:
            self.log.info('Opening existing project' + self.filename)
            try:
                f = open(self.filename, 'rb')
                self.data = pickle.load(f)
            except:
                # Intentionally broad 'except' clause, because opening something
                # that isn't a pickle file can cause all kinds of errors...
                self.log.error('Unable to load project ' + self.filename)
                self.filename = None
                self.data = dict()
            finally:
                f.close()
        else:
            self.log.info('Creating new project')
            self.data = dict()

    def save(self, save_as=False):
        """
        Save the project.

        :return:    True if project was saved, False otherwise
        """
        # If running in batch mode, no parent window for file dialogs
        if self.window is None:
            self.log.error('Cannot save project in batch mode')
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

        # Attempt to save the file atomically
        tmpfilename = self.filename + '.tmp'
        try:
            f = open(tmpfilename, 'wb')
            pickle.dump(self.data, f)
        except IOError:
            wx.MessageBox('Failed to save project', '', wx.OK|wx.ICON_ERROR, self.window)
            return False
        finally:
            f.close()
        shutil.move(tmpfilename, self.filename)

        self.log.info('Saved project ' + self.filename)
        return True
