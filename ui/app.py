################################################################################
# The main application handler
################################################################################

# Set up logging
import logging
import sys
try:
    if sys.frozen:
        # If we are running standalone, don't annoy the user with pointless debug
        # messages
        logging.basicConfig(
            level = logging.CRITICAL,
            format = '%(levelname)-8s %(message)s'
        )
    else:
        logging.basicConfig(
            level = logging.DEBUG,
            format = '%(levelname)-8s %(message)s'
        )
except AttributeError:
    logging.basicConfig(
        level = logging.DEBUG,
        format = '%(levelname)-8s %(message)s'
    )


# The application
import wx
import shelve
import os

import util
import dose
import config

class Application(wx.App):
    def OnInit(self):
        self.SetAppName('DO3SE')
        self.title = 'DO3SE Model'

        # Only allow one instance of the program
        self.sichecker = wx.SingleInstanceChecker(
                "%s-%s.lock" % (self.GetAppName(), wx.GetUserId()),
                wx.StandardPaths_Get().GetTempDir())

        if self.sichecker.IsAnotherRunning():
            logging.error("Another instance is already running, exiting.")
            return False

        # Make sure configuration directory exists
        if not os.path.exists(wx.StandardPaths_Get().GetUserDataDir()):
            os.makedirs(wx.StandardPaths_Get().GetUserDataDir())
            logging.info("Created configuration directory "
                    + wx.StandardPaths_Get().GetUserDataDir())

        # Open configuration file
        configpath = os.path.join(wx.StandardPaths_Get().GetUserDataDir(), 'config.json')
        logging.info("Loading configuration file " + configpath)
        self.config = config.open_config(configpath)

        # Sanitise configuration file
        config.sanitise_config(self.config)
        self.config.sync()
        
        return True


    def AddFileToHistory(self, path):
        """Add a path to recent file history

        Adds the path to the file history list, removing duplicates and making sure
        the list is only 9 items long and in chronological order.
        """
        # Remove duplicates
        try:
            self.config['file_history'].remove(path)
        except ValueError:
            pass
        # Add path
        self.config['file_history'].append(path)
        # Trim to 9 items
        self.config['file_history'] = self.config['file_history'][-9:]
        # Save the config
        self.config.sync()

        logging.debug("Added file to history: " + path)


    def OnExit(self):
        """Clean up on exit

        Clean up configurating, SingleInstanceChecker, etc. on application exit
        """
        self.config.close()
        logging.debug("Configuration file closed")
        del self.sichecker


    def Run(self):
        import ui
        self.toplevel = ui.MainWindow()
        self.toplevel.Bind(wx.EVT_CLOSE, lambda evt: self.Exit())
        self.toplevel.Show()
        self.MainLoop()


    def Exit(self):
        # do some stuff
        wx.App.Exit(self)



app = Application(False)
