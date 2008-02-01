################################################################################
# The main application handler
################################################################################

# Configuration file version
CFGVERSION = "0.4"

# Set up logging
import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)-8s %(message)s'
)


# The application
import wx
import shelve
import os

import util

class Application(wx.App):
    def OnInit(self):
        self.SetAppName('DOSE')

        # Single instance checker - only allow one instance of the program
        self.sichecker = wx.SingleInstanceChecker("%s-%s.lock" % 
                (self.GetAppName(), wx.GetUserId()))
        if self.sichecker.IsAnotherRunning():
            logging.error("Another instance is already running, exiting.")
            return False

        self._config_load()

        return True


    def _config_load(self):
        dirname = wx.StandardPaths_Get().GetUserDataDir()
        path = os.path.join(dirname, 'dose.cfg')
        logging.info("Using configuration file '%s'" % path)

        if not os.path.exists(dirname):
            os.mkdir(dirname)
            logging.debug("Created directory '%s'" % dirname)

        self.config = shelve.open(os.path.join(dirname, 'dose.cfg'))

        if (not 'version' in self.config) \
                or (util.versioncmp(CFGVERSION, self.config['version'])):
            logging.info("Upgrading configuration file ...")
            self._config_init()


    def _config_init(self):
        if not 'filehistory' in self.config:
            self.config['filehistory'] = list([])
        if not 'preset.inputs' in self.config:
            self.config['preset.inputs'] = dict([])
        if not 'preset.outputs' in self.config:
            self.config['preset.outputs'] = dict([])
        if not 'preset.site' in self.config:
            self.config['preset.site'] = dict([])
        if not 'preset.veg' in self.config:
            self.config['preset.veg'] = dict([])
        self.config['version'] = CFGVERSION


    def AddFileToHistory(self, path):
        """Add a path to recent file history

        Adds the path to the file history list, removing duplicates and making sure
        the list is only 9 items long and in chronological order.
        """
        d = self.config['filehistory']
        try:
            d.remove(path)
        except ValueError:
            pass
        d.append(path)
        d = d[-9:]
        self.config['filehistory'] = d


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
