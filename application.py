from tools import _verbose

import wx
from wx import xrc
import os

import config
from mainwindow import MainWindow

_verbose("Initializing application...")

xrcres = xrc.XmlResource("do3se.xrc")
toplevel = None

class Application(wx.App):
    """Main application class.

    Loads the main window.
    """
    def OnInit(self):
        global xrcres, toplevel

        self.frame = toplevel = MainWindow()
        self.frame.Show()

        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)

        from resultswindow import ResultsWindow
        foo = ResultsWindow(None)
        foo.Show()

        return True

    def OnClose(self, evt):
        """Clean-up when closing the application.
        """
        _verbose("Exiting application...")
        # Put shut-down stuff here
        config.Write()
        self.Exit()
