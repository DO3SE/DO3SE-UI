import wx
from wx import xrc
import os

from tools import _verbose
import wxext
import config
import inputfile
import F as do3se

class MainWindow(wx.Frame):
    """Main application window.

    This is where all the input, parameterisation etc. happens before running
    the model and showing the outputs.
    """

    def __init__(self, res):
        """Constructor

        Initialise the window (via the smaller Init* procedures)
        """

        wx.Frame.__init__(self, None)
        self.res = res

        # Local variables
        self.open_prev_dir = ""
        self.inputfile = None

        self.InitFrame()
        self.InitMenu()
        self.InitFinal()


    def InitFrame(self):
        """Initialise everything except for the menu.

        Get the main panel from the XRC, get references to all of the important
        controls, bind controls to actions.
        """

        # Get the main panel
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(mainsizer)
        self.panel = self.res.LoadPanel(self, 'window_main')
        mainsizer.Add(self.panel, 1, wx.EXPAND)
        self.menubar = self.res.LoadMenuBar('menu')
        self.SetMenuBar(self.menubar)

        # Set some frame attributes
        self.SetSize((600, 400))
        self.SetTitle('Deposition of Ozone and Stomatal Exchange')

        # Get the 2 exchangable panels
        self.panel_placeholder = xrc.XRCCTRL(self, 'panel_placeholder')
        self.panel_main = xrc.XRCCTRL(self, 'panel_main')


        # --- 'Input' panel ---
        self.input_filename = xrc.XRCCTRL(self, 'text_inputfile')
        self.input_fields = xrc.XRCCTRL(self, 'panel_input_fields')
        self.input_fields.SetAvailable(['Hour', 'Day of Month', 'Month', 'Day of Year', 'Year', 'Temperature'])
        self.input_fields.SetSelected(['Day of Year', 'Hour'])
        self.Bind(wx.EVT_BUTTON, self.OnFileOpen, id = xrc.XRCID('button_change_file'))
        

        # --- 'Site' panel  ---
        self.site_latitude = xrc.XRCCTRL(self, 'float_site_latitude')
        self.site_longitude = xrc.XRCCTRL(self, 'float_site_longitude')
        self.site_elevation = xrc.XRCCTRL(self, 'spin_site_elevation')

        self.site_latitude.SetRange(-90.0, 90.0)
        self.site_longitude.SetRange(-180.0, 180.0)

        # Bind parameters to input controls
        self.site_latitude.Bind(wx.EVT_KILL_FOCUS, 
                lambda evt: do3se.SetSiteParam('latitude', self.site_latitude.GetFloat()))
        self.site_longitude.Bind(wx.EVT_KILL_FOCUS, 
                lambda evt: do3se.SetSiteParam('longitude', self.site_longitude.GetFloat()))


        # Bind other events and controls
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.Close(), 
                id = xrc.XRCID('button_quit'))
        #self.Bind(wx.EVT_BUTTON, self.OnRun, id = xrc.XRCID('button_run'))


    def InitMenu(self):
        """Initialise the menu.

        Bind menu items to their actions, and generally get the menu ready
        to be used.
        """

        self.Bind(wx.EVT_MENU, self.OnFileOpen, id = xrc.XRCID('menu_file_open'))
        self.Bind(wx.EVT_MENU, self.OnFileClose, id = xrc.XRCID('menu_file_close'))
        self.Bind(wx.EVT_MENU, lambda evt: self.Close(), 
                id = xrc.XRCID('menu_file_quit'))

        self.RefreshOpenRecent()


    def InitFinal(self):
        """Final initialisation actions.

        Do anything initialisation-wise that needs to be done last.
        """

        # Show only the placeholder panel on startup
        self.panel_placeholder.Show()
        self.panel_main.Hide()


    def RefreshOpenRecent(self):
        """Reload the 'Open recent' submenu."""

        # Get the submenu
        recent = self.menubar.FindItemById(xrc.XRCID('menu_file_openrecent')).GetSubMenu()

        # Empty the submenu
        for i in recent.GetMenuItems():
            recent.RemoveItem(i)

        # Add the entries
        for r in config.GetRecentFiles():
            id = wx.NewId()
            recent.Append(id, r)
            self.Bind(wx.EVT_MENU, lambda evt: self.LoadFile(r), id = id)
        

    def OnClose(self, evt):
        """On-close cleanup."""
        
        # Extra cleanup stuff goes here
        evt.Skip()


    def OnFileOpen(self, evt):
        """Show 'Open data file' dialog and load selected file."""

        # Show the dialog
        fd = wx.FileDialog(self, message = 'Open data file', 
                defaultDir = self.open_prev_dir, 
                wildcard = 'Comma-Separated Values (*.csv)|*.csv|All files (*.*)|*.*', 
                style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        fd.ShowModal()
        
        path = fd.GetPath()

        self.open_prev_dir = os.path.dirname(path)
        self.LoadFile(path)


    def OnFileClose(self, evt):
        # TODO: An are-you-sure check if site/veg/calc parameters haven't 
        #       been saved yet.
        self.inputfile = None
        self.panel_main.Hide()
        self.panel_placeholder.Show()
        self.Layout()
        self.menubar.FindItemById(xrc.XRCID('menu_file_close')).Enable(False)
        foo = wxext.ChoiceDialog(self, 'Choose', [1, 2, 3])
        foo.ShowModal()


    def LoadFile(self, path):
        """Load data file.

        Loads a data file specified by 'path' and adds it to the recent files
        list.
        """

        if not os.path.isfile(path):
            wx.MessageBox('No file selected!', 'DO3SE', wx.OK | wx.ICON_ERROR)
            config.RemoveRecentFile(path)
            self.RefreshOpenRecent()

        elif not os.access(path, os.R_OK):
            wx.MessageBox('Could not read the specified file!', 'DO3SE', 
                    wx.OK | wx.ICON_ERROR)
            # Remove recent file from menu
            config.RemoveRecentFile(path)
            self.RefreshOpenRecent()
            
        else:
            # Prompt use for closing old file if one is already open
            if not self.inputfile or \
                    wx.MessageBox('Close the current data file?', 
                            'DO3SE', wx.YES_NO | wx.ICON_QUESTION) == wx.YES:
                _verbose('Loading data file ' + path)
                self.inputfile = inputfile.InputFile(path)
                # Show main panel
                self.panel_placeholder.Hide()
                self.panel_main.Show()
                # Resize widgets
                self.Layout()
                # Update filename display
                self.input_filename.SetValue(path)
                # Enable 'Close' on menu
                self.menubar.FindItemById(xrc.XRCID('menu_file_close')).Enable(True)
                # Add recent file entry
                config.AddRecentFile(path)
                # Refresh menu
                self.RefreshOpenRecent()
