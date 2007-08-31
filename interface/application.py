from tools import _verbose

import wx
from wx import xrc
import os

import config

_verbose("Initializing application...")

class Application(wx.App):
    """Main application class.

    Loads the main window.
    """
    def OnInit(self):
        self.res = xrc.EmptyXmlResource()
        self.res.LoadFromString(open("do3se.xrc").read())

        from mainwindow import MainWindow

        self.frame = MainWindow(self.res)
        self.frame.Show()

        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)

        return True

    def OnClose(self, evt):
        """Clean-up when closing the application.
        """
        _verbose("Exiting application...")
        # Put shut-down stuff here
        config.Write()
        self.Exit()
