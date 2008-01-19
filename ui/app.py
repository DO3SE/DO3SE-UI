################################################################################
# The main application handler
################################################################################

# Set up logging
import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(levelname)-8s %(message)s'
)


# The application
import wx
from ui import MainWindow

class Application(wx.App):
    def OnInit(self):
        self.main = MainWindow()
        self.main.Bind(wx.EVT_CLOSE, lambda evt: self.Exit())
        self.main.Show()
        return True
