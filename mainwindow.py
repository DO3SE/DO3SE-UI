import wx
from wx import xrc
import os

from tools import _verbose
import wxext
import config
import inputfile
import maps
import dose

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
        self.input_presets = xrc.XRCCTRL(self, 'preset_input')
        self.input_fields.SetAvailable([maps.input_field_map[x] for x in maps.input_fields])
        # Setup the PresetChooser
        self.input_presets.SetPresets(config.state['presets']['input'])
        self.input_presets.do_load = self.input_fields.SetSelection
        self.input_presets.do_get = self.input_fields.GetSelection
        self.Bind(wx.EVT_BUTTON, self.OnFileOpen, id = xrc.XRCID('button_change_file'))
        

        # --- 'Site' panel  ---
        # Setup the PresetChooser
        self.site_presets = xrc.XRCCTRL(self, 'preset_site')
        self.site_presets.SetPresets(config.state['presets']['site'])
        self.site_presets.do_load = self.SetSiteParams
        self.site_presets.do_get = self.GetSiteParams
        
        # Bind the controls
        self.site_o3zr = xrc.XRCCTRL(self, 'spin_site_o3zr')
        self.site_uzr = xrc.XRCCTRL(self, 'spin_site_uzr')
        self.site_xzr = xrc.XRCCTRL(self, 'spin_site_xzr')
        self.site_o3canopy = xrc.XRCCTRL(self, 'spin_site_o3canopy')
        self.site_o3same = xrc.XRCCTRL(self, 'check_site_o3same')
        self.Bind(wx.EVT_CHECKBOX, 
                lambda evt: self.site_o3canopy.Enable(not self.site_o3same.IsChecked()),
                self.site_o3same)
        self.site_metcanopy = xrc.XRCCTRL(self, 'spin_site_metcanopy')
        self.site_metsame = xrc.XRCCTRL(self, 'check_site_metsame')
        self.Bind(wx.EVT_CHECKBOX, 
                lambda evt: self.site_metcanopy.Enable(not self.site_metsame.IsChecked()),
                self.site_metsame)
        self.site_latitude = xrc.XRCCTRL(self, 'float_site_latitude')
        self.site_longitude = xrc.XRCCTRL(self, 'float_site_longitude')
        self.site_elevation = xrc.XRCCTRL(self, 'spin_site_elevation')
        self.site_rsoil = xrc.XRCCTRL(self, 'spin_site_rsoil')
        self.site_soil = xrc.XRCCTRL(self, 'choice_site_soil')

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
        self.Bind(wx.EVT_BUTTON, self.OnRun, id = xrc.XRCID('button_run'))


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


    def LoadFile(self, path):
        """Load data file.

        Loads a data file specified by 'path' and adds it to the recent files
        list.
        """

        if not os.path.isfile(path):
            wx.MessageBox('No file selected!', 'DO3SE', wx.OK | wx.ICON_ERROR, self)
            config.RemoveRecentFile(path)
            self.RefreshOpenRecent()

        elif not os.access(path, os.R_OK):
            wx.MessageBox('Could not read the specified file!', 'DO3SE', 
                    wx.OK | wx.ICON_ERROR, self)
            # Remove recent file from menu
            config.RemoveRecentFile(path)
            self.RefreshOpenRecent()
            
        else:
            # Prompt use for closing old file if one is already open
            if not self.inputfile or \
                    wx.MessageBox('Close the current data file?', 'DO3SE', 
                        wx.YES_NO | wx.ICON_QUESTION, self) == wx.YES:
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


    def SetSiteParams(self, params):
        self.site_o3zr.SetValue(params['o3zr'])
        self.site_uzr.SetValue(params['uzr'])
        self.site_xzr.SetValue(params['xzr'])

        if params['o3_h'] == -1.0:
            self.site_o3same.SetValue(True)
            self.site_o3canopy.Enable(False)
        else:
            self.site_o3same.SetValue(False)
            self.site_o3canopy.Enable(True)
            self.site_o3canopy.SetValue(params['o3_h'])

        if params['u_h'] == -1.0:
            self.site_metsame.SetValue(True)
            self.site_metcanopy.Enable(False)
        else:
            self.site_metsame.SetValue(False)
            self.site_metcanopy.Enable(True)
            self.site_metcanopy.SetValue(params['u_h'])

        self.site_latitude.SetValue(params['lat'])
        self.site_longitude.SetValue(params['lon'])
        self.site_elevation.SetValue(params['elev'])
        self.site_rsoil.SetValue(params['rsoil'])
        self.site_soil.SetStringSelection(
                {-4.0: 'Coarse', -5.5: 'Medium', -7.0: 'Fine'}[params['soil_a']])


    def GetSiteParams(self):
        data = {
                'o3zr'      : float(self.site_o3zr.GetValue()),
                'uzr'       : float(self.site_uzr.GetValue()),
                'xzr'       : float(self.site_xzr.GetValue()),
                'o3_h'      : float(self.site_o3canopy.GetValue()),
                'u_h'       : float(self.site_metcanopy.GetValue()),
                'lat'       : self.site_latitude.GetFloat(),
                'lon'       : self.site_longitude.GetFloat(),
                'elev'      : float(self.site_elevation.GetValue()),
                'rsoil'     : float(self.site_rsoil.GetValue()),
                'soil_bd'   : 1.3,
                'soil_a'    : {'Coarse': -4.0, 'Medium': -5.5, 'Fine': -7.0}[self.site_soil.GetStringSelection()], 
                'soil_b'    : {'Coarse': -2.3, 'Medium': -3.3, 'Fine': -5.4}[self.site_soil.GetStringSelection()], 
                'fc_m'      : 0.193,
                }

        if self.site_o3same.IsChecked(): data['o3_h'] = -1.0
        if self.site_metsame.IsChecked(): data['u_h'] = -1.0

        return data;
        

    def OnRun(self, evt):
        print "foo"
        self.inputfile.SetFields(maps.InputFieldsToShort(self.input_fields.GetSelection()))
        self.inputfile.Load()
        # Deal with problems loading the file here
        
        # Build site params
        site = {
                'rsoil'     : float(self.site_rsoil.GetValue()),
                'soil_bd'   : 1.3,
                'soil_a'    : {'Coarse': -4.0, 'Medium': -5.5, 'Fine': -7.0}[self.site_soil.GetChoice()], 
                'soil_b'    : {'Coarse': -2.3, 'Medium': -3.3, 'Fine': -5.4}[self.site_soil.GetChoice()], 
                'fc_m'      : 0.193,
                }

        veg = {
                't_min'     : float(self.veg_t_min.GetValue()),
                't_opt'     : float(self.veg_t_opt.GetValue()),
                't_max'     : float(self.veg_t_max.GetValue()),
                'vpd_min'   : float(self.veg_vpd_min.GetValue()),
                'vpd_min'   : float(self.veg_vpd_min.GetValue()),
                'vpd_min'   : float(self.veg_vpd_min.GetValue()),
                'vpd_min'   : float(self.veg_vpd_min.GetValue()),

                }

