app_name = 'DO3SE'
app_description = 'Deposition of Ozone and Stomatal Exchange'
app_version = '2.0-alpha'

import sys
import os.path
import logging
_log = logging.getLogger('do3se.application')

import wx

from util import load_presets
from config import Config

class App(wx.App):
    """DO3SE application.

    A wrapper around wx.App to handle all of the application-specific setup,
    tear-down, configuration handling etc.
    """

    def OnInit(self):
        """Set up application instance."""

        self.SetAppName(app_name)
        self.title = app_name

        # Figure out some paths...
        si_filename = '%s-%s.lock' % (self.GetAppName(), wx.GetUserId())
        config_path = os.path.join(wx.StandardPaths_Get().GetUserDataDir(), 'config.pickle')

        # Only allow one instance of the application
        self.sichecker = wx.SingleInstanceChecker(si_filename, wx.StandardPaths_Get().GetTempDir())
        if self.sichecker.IsAnotherRunning():
            _log.error("Another instance is already running - exiting!")
            wx.MessageDialog(None, "DO3SE is already running", style=wx.OK|wx.ICON_ERROR).ShowModal()
            return False

        # Make sure configuration directory exists
        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path))
            _log.info("Created configuration directory: " + os.path.dirname(config_path))

        # Load configuration
        self.config = Config(config_path)
        # Load default presets
        self.default_presets = load_presets(open('resources/default_veg_presets.csv', 'r'))

        # Keep track of existing project windows - ProjectWindow instances add
        # and remove themselves from this
        self.windows = set()

        return True

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


def main(args):
    from ui import MainWindow
    # If the app is frozen (i.e. made into an executable), don't annoy the user
    # with log messages they don't care about.
    if hasattr(sys, 'frozen') and sys.frozen:
        level = logging.CRITICAL
    else:
        level = logging.DEBUG
    logging.basicConfig(format="[%(levelname)-8s] %(name)s: %(message)s",
                        level=level)
    app = App()
    w = MainWindow(app)
    w.Show()
    app.MainLoop()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
