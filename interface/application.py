from tools import _verbose

import wx
from wx import xrc
import os

import inputfile
import config
from wxext import FloatCtrl

_verbose("Initializing application...")

class Application(wx.App):
    def OnInit(self):
        self.res = xrc.EmptyXmlResource()
        self.res.LoadFromString(open("do3se.xrc").read())

        self.InitFrame()
        self.InitMenu()
        self.InitFinal()

        self.open_prev_dir = ""
        self.inputfile = None
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
        self.float_site_latitude = xrc.XRCCTRL(self.frame, 'float_site_latitude')
        self.float_site_longitude = xrc.XRCCTRL(self.frame, 'float_site_longitude')
        self.float_site_latitude.SetRange(-90.0, 90.0)
        self.float_site_longitude.SetRange(-180.0, 180.0)

    def InitMenu(self):
        """Bind menu items to their actions.
        """

        self.Bind(wx.EVT_MENU, self.OnMenuFileOpen, id = xrc.XRCID('menu_file_open'))
        self.Bind(wx.EVT_MENU, self.OnClose, id = xrc.XRCID('menu_file_quit'))

        self.InitMenuOpenRecent()

    def InitMenuOpenRecent(self):
        # Get the submenu
        recent = self.frame.GetMenuBar().FindItemById(xrc.XRCID('menu_file_openrecent')).GetSubMenu()

        # Empty the submenu
        for i in recent.GetMenuItems():
            recent.RemoveItem(i)
        
        for r in config.GetRecentFiles():
            id = wx.NewId()
            recent.Append(id, r)
            self.Bind(wx.EVT_MENU, lambda evt: self.LoadFile(r), id = id)

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
        config.Write()
        self.Exit()

    def OnMenuFileOpen(self, evt):
        """Opening a new datafile.
        """
        fd = wx.FileDialog(self.frame, message = "Open data file", defaultDir = self.open_prev_dir, \
                wildcard = "Comma-Separated Values (*.csv)|*.csv|All files (*.*)|*.*", \
                style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fd.ShowModal()

        path = fd.GetPath()

        if not path:
            md = wx.MessageDialog(self.frame, "No file selected!", "DO3SE", style = wx.OK | wx.ICON_ERROR)
            md.ShowModal()

        else:
            self.open_prev_dir = os.path.dirname(path)
            self.inputfile = inputfile.InputFile(path)
            self.LoadFile(path)

    def LoadFile(self, path):
        _verbose("Loading data file " + path)
        if not os.access(path, os.R_OK):
            md = wx.MessageDialog(self.frame, "File does not exist or is not readable!", \
                    "DO3SE", style = wx.OX | wx.ICON_ERROR)
            md.ShowModal()

        else:
            self.panel_placeholder.Hide()
            self.panel_main.Show()
            self.text_inputfile.SetValue(path)
            self.frame.Layout()
            self.frame.GetMenuBar().FindItemById(xrc.XRCID("menu_file_close")).Enable(True)
            config.AddRecentFile(path)
            self.InitMenuOpenRecent()

