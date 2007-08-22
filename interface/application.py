from tools import _verbose

import wx
from wx import xrc
import os

import state
import inputfile
import config
from floatspin import FloatSpin

_verbose("Initializing application...")

class Application(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource('do3se.xrc')
        self.InitFrame()
        self.InitMenu()
        self.InitFinal()
        return True

    def InitFrame(self):
        # Get the main window
        self.frame = self.res.LoadFrame(None, "window_main")
        self.frame.SetSize((600, 400))
        # Hook the various important controls
        self.panel_placeholder = xrc.XRCCTRL(self.frame, 'panel_placeholder')
        self.panel_placeholder.Show()
        self.panel_main = xrc.XRCCTRL(self.frame, 'panel_main')
        self.panel_main.Hide()

        self.panel_input = xrc.XRCCTRL(self.frame, 'panel_input')
        self.text_inputfile = xrc.XRCCTRL(self.frame, 'text_inputfile')

        self.panel_site = xrc.XRCCTRL(self.frame, 'panel_site')
        #self.floatspin_latitude = FloatSpin(self.panel_site)
        #self.res.AttachUnknownControl('floatspin_latitude', self.floatspin_latitude, self.panel_site)
        #self.frame.Layout()
        pass

    def InitMenu(self):
        """Bind menu items to their actions.
        """
        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, id = xrc.XRCID('menu_file_open'))
        self.Bind(wx.EVT_MENU, self.OnClose, id = xrc.XRCID('menu_file_quit'))
        pass

    def InitFinal(self):
        """Other event bindings, etc.
        """

        # Other close events
        self.frame.Bind(wx.EVT_CLOSE, self.OnClose)
        self.frame.Bind(wx.EVT_BUTTON, self.OnClose, id = xrc.XRCID('button_quit'))

        self.frame.Bind(wx.EVT_BUTTON, self.OnMenuFileOpen, id = xrc.XRCID('button_change_file'))
        
        # Show the main window
        self.frame.Show()

    def OnClose(self, evt):
        """Clean-up when closing the application.
        """
        _verbose("Exiting application...")
        # Put shut-down stuff here
        self.Exit()

    def OnMenuFileOpen(self, evt):
        """Opening a new datafile.
        """
        fd = wx.FileDialog(self.frame, message = "Open data file", defaultDir = state.open_prev_dir, \
                wildcard = "Comma-Separated Values (*.csv)|*.csv|All files (*.*)|*.*", \
                style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fd.ShowModal()

        path = fd.GetPath()

        if path and os.access(path, os.R_OK):
            state.open_prev_dir = os.path.dirname(path)
            state.inputfile = inputfile.InputFile(path)

            self.panel_placeholder.Hide()
            self.panel_main.Show()
            self.text_inputfile.SetValue(path)
            self.frame.Layout()

        else:
            md = wx.MessageDialog(self.frame, "No file selected!", "DO3SE", style = wx.OK | wx.ICON_ERROR)
            md.ShowModal()
