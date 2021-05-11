from do3se.config import Config
from do3se.util import load_presets
import resources
import wx
import logging
import optparse
import os.path
app_name = 'DO3SE'
app_description = 'Deposition of Ozone and Stomatal Exchange'
app_version = '3.2.0'

_log = logging.getLogger('do3se.application')


class App(wx.App):
    """DO3SE application.

    A wrapper around wx.App to handle all of the application-specific setup,
    tear-down, configuration handling etc.
    """

    def OnInit(self):
        """Set up application instance."""

        self.SetAppName(app_name)
        self.title = app_name

        # Only allow one instance of the application
        si_filename = '%s-%s.lock' % (self.GetAppName(), wx.GetUserId())
        self.sichecker = wx.SingleInstanceChecker(
            si_filename, wx.StandardPaths.Get().GetTempDir())
        if self.sichecker.IsAnotherRunning():
            _log.error("Another instance is already running - exiting!")
            wx.MessageDialog(None, "DO3SE is already running",
                             style=wx.OK | wx.ICON_ERROR).ShowModal()
            return False

        # Load configuration
        self.config = open_config()
        # Load default presets
        self.default_presets = load_presets(
            resources.get_memoryfs_stream('resources/default_veg_presets.csv'))

        # Keep track of existing project windows - ProjectWindow instances add
        # and remove themselves from this
        self.windows = set()

        # Set up context help provider
        wx.HelpProvider.Set(wx.SimpleHelpProvider())

        return True

    def IsProjectOpen(self, filename):
        """Check if another project window has *filename* open."""
        filename = os.path.abspath(filename)
        for w in self.windows:
            if w.project.exists():
                if os.path.abspath(w.project.filename) == filename:
                    return True
        return False

    def OnExit(self):
        """Application clean-up when exiting."""
        self.config.save()
        del self.sichecker

    def Quit(self):
        """Close all project windows and exit application.

        This method calls the :meth:`Close` method on each open window.  If all
        windows are successfully closed then :class:`wx.App`'s own exit
        mechanism will end the application.
        """
        # Need to duplicate set of windows, set will change during iteration
        for w in set(self.windows):
            w.Close()


def open_config():
    """Open configuration file as a :class:`~do3se.config.Config` object.

    Because this function uses :obj:`wx.StandardPaths`, an application object
    with a valid application name must be created first.
    """
    # Find path where the config file should be
    filename = os.path.join(wx.StandardPaths.Get().GetUserDataDir(),
                            'config.pickle')
    # Create config directory if it doesn't exist
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        _log.info('Created configuration directory: ' + dirname)
    # Create and return Config object
    return Config(filename)


def logging_setup(**kwargs):
    """Setup Python logging.

    *kwargs* are merged with default options and then passed to
    :func:`logging.basicConfig`.  This function exists so that different
    methods of running the application can use the same logging setup without
    duplication.
    """
    config = {'format': '[%(levelname)-8s] %(name)s: %(message)s',
              'level': logging.DEBUG}
    config.update(kwargs)
    logging.basicConfig(**config)


def main(args):
    from ui import MainWindow, ProjectWindow

    parser = optparse.OptionParser(usage='Usage: %prog [options] ...')
    parser.add_option('-v', '--verbose',
                      action='store_const',
                      dest='loglevel',
                      const=logging.INFO)
    parser.add_option('-d', '--debug',
                      action='store_const',
                      dest='loglevel',
                      const=logging.DEBUG)
    parser.set_defaults(loglevel=logging.CRITICAL)

    (options, args) = parser.parse_args(args)

    logging_setup(level=options.loglevel)

    # Show a project window for each argument, or launch the main window
    app = App()
    if len(args) > 0:
        for filename in args:
            w = ProjectWindow(app, filename)
            w.Show()
    else:
        w = MainWindow(app)
        w.Show()
    app.MainLoop()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
