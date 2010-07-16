app_name = 'DO3SE'
app_description = 'Deposition of Ozone and Stomatal Exchange'
app_version = '2.0-alpha'

import wx
import os.path
import logging

from config import Config

class App(wx.App):
    """
    DO3SE application

    A wrapper around wx.App to handle all of the application-specific setup,
    tear-down, configuration handling etc.
    """

    def OnInit(self):
        """
        Set up application instance
        """

        self.SetAppName(app_name)
        self.title = app_name

        # Figure out some paths...
        si_filename = '%s-%s.lock' % (self.GetAppName(), wx.GetUserId())
        config_path = os.path.join(wx.StandardPaths_Get().GetUserDataDir(), 'config.json')

        # Only allow one instance of the application
        self.sichecker = wx.SingleInstanceChecker(si_filename, wx.StandardPaths_Get().GetTempDir())
        if self.sichecker.IsAnotherRunning():
            logging.error("Another instance is already running - exiting!")
            wx.MessageDialog(None, "DO3SE is already running", style=wx.OK|wx.ICON_ERROR).ShowModal()
            return False

        # Make sure configuration directory exists
        if not os.path.exists(os.path.dirname(config_path)):
            os.makedirs(os.path.dirname(config_path))
            logging.info("Created configuration directory: " + os.path.dirname(config_path))

        # Open configuration file
        self.config = Config(config_path, 'resources/default_veg_presets.csv')

        return True


    def OnExit(self):
        """
        Application clean-up when exiting
        """
        self.config.close()
        del self.sichecker


    def Run(self):
        """
        Run application
        """
        from mainwindow import MainWindow
        self.toplevel = MainWindow(self)
        self.toplevel.Bind(wx.EVT_CLOSE, lambda evt: self.Exit())
        self.toplevel.Show()
        self.MainLoop()
