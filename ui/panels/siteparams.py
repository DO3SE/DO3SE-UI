import wx

from .. import wxext
from ..FloatSpin import FloatSpin
from ..app import logging, app

class SiteParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Dict to contain the actual input controls
        self.fields = dict()

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.ALL|wx.EXPAND, 6)
        self.presets.SetPresets(app.config['preset.site'])
        # Get/set callbacks
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues
        # Force a sync of the config on a preset change
        def f():
            app.config['preset.site'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f
        
        # FlexGridSizer for the sections
        sSiteParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sSiteParams.AddGrowableCol(0)
        sSiteParams.AddGrowableCol(1)
        s.Add(sSiteParams, 0, wx.ALL|wx.EXPAND, 6)
        
        # Location parameters
        sLocation = wxext.StaticBox2Col(self, "Location")
        sSiteParams.Add(sLocation, 0, wx.EXPAND)
        sLocation.fgs.Add(wx.StaticText(self, label="Latitude"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lat'] = FloatSpin(self, value=45.0, 
                min_val=-90.0, max_val=90.0, increment=0.1, digits=3)
        sLocation.fgs.Add(self.fields['lat'], 0)
        sLocation.fgs.Add(wx.StaticText(self, label="Longitude"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lon'] = FloatSpin(self, value=0.0,
                min_val=-180.0, max_val=180.0, increment=0.1, digits=3)
        sLocation.fgs.Add(self.fields['lon'], 0)
        sLocation.fgs.Add(wx.StaticText(self, label="Elevation"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['elev'] = wx.SpinCtrl(self, min=-100, max=5000, initial=0)
        sLocation.fgs.Add(self.fields['elev'], 0)

        # Measurement heights
        sHeights = wxext.StaticBox2Col(self, "Measurement heights")
        sSiteParams.Add(sHeights, 0, wx.EXPAND)
        sHeights.fgs.Add(wx.StaticText(self, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['o3zr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['o3zr'], 0)
        sHeights.fgs.Add(wx.StaticText(self, label="Meteorological data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['uzr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['uzr'], 0)
        sHeights.fgs.Add(wx.StaticText(self, label="Other data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['xzr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['xzr'], 0)

        # Soil properties
        sSoil = wxext.StaticBox2Col(self, "Soil")
        sSiteParams.Add(sSoil, 0, wx.EXPAND)
        sSoil.fgs.Add(wx.StaticText(self, label="Texture"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['soil_tex'] = wx.Choice(self, 
                choices=['Fine', 'Medium', 'Coarse'])
        self.fields['soil_tex'].SetStringSelection('Medium')
        sSoil.fgs.Add(self.fields['soil_tex'], 0)
        sSoil.fgs.Add(wx.StaticText(self, label="Rsoil"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['rsoil'] = wx.SpinCtrl(self, min=1, max=1000, initial=200)
        sSoil.fgs.Add(self.fields['rsoil'], 0)

        # Canopy heights
        sCanopies = wxext.StaticBox2Col(self, "Canopy heights")
        sSiteParams.Add(sCanopies, 0, wx.EXPAND)
        sCanopies.fgs.Add(wx.StaticText(self, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteO3Canopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteO3Canopy, 0)
        self.fields['o3_h'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sSiteO3Canopy.Add(self.fields['o3_h'], 0, wx.RIGHT, 6)
        self.fields['o3_h_copy'] = wx.CheckBox(self, label="Same as target canopy")
        sSiteO3Canopy.Add(self.fields['o3_h_copy'], 0)
        self.fields['o3_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.fields['o3_h'].Enable(not self.fields['o3_h_copy'].IsChecked()),
                self.fields['o3_h_copy'])
        sCanopies.fgs.Add(wx.StaticText(self, label="Meteorological data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteMetCanopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteMetCanopy, 0)
        self.fields['u_h'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sSiteMetCanopy.Add(self.fields['u_h'], 0, wx.RIGHT, 6)
        self.fields['u_h_copy'] = wx.CheckBox(self, label="Same as target canopy")
        sSiteMetCanopy.Add(self.fields['u_h_copy'], 0)
        self.fields['u_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.fields['u_h'].Enable(not self.fields['u_h_copy'].IsChecked()),
                self.fields['u_h_copy'])


    def getvalues(self):
        return {
            'lat'       : float(self.fields['lat'].GetValue()),
            'lon'       : float(self.fields['lon'].GetValue()),
            'elev'      : float(self.fields['elev'].GetValue()),
            'o3zr'      : float(self.fields['o3zr'].GetValue()),
            'uzr'       : float(self.fields['uzr'].GetValue()),
            'xzr'       : float(self.fields['xzr'].GetValue()),
            'o3_h'      : float(self.fields['o3_h'].GetValue()),
            'u_h'       : float(self.fields['u_h'].GetValue()),
            'o3_h_copy' : self.fields['o3_h_copy'].GetValue(),
            'u_h_copy'  : self.fields['u_h_copy'].GetValue(),
            'rsoil'     : float(self.fields['rsoil'].GetValue()),
            'soil_a'    : {'Coarse': -4.0, 'Medium': -5.5, 'Fine': -7.0}
                            [self.fields['soil_tex'].GetStringSelection()],
            'soil_b'    : {'Coarse': -2.3, 'Medium': -3.3, 'Fine': -5.4}
                            [self.fields['soil_tex'].GetStringSelection()],
            'soil_bd'   : {'Coarse': 1.6, 'Medium': 1.3, 'Fine': 1.1}
                            [self.fields['soil_tex'].GetStringSelection()],
            'fc_m'      : {'Coarse': 0.107, 'Medium': 0.193, 'Fine': 0.339}
                            [self.fields['soil_tex'].GetStringSelection()],
        }


    def setvalues(self, v):
        self.fields['lat'].SetValue(v['lat'])
        self.fields['lon'].SetValue(v['lon'])
        self.fields['elev'].SetValue(v['elev'])
        self.fields['o3zr'].SetValue(v['o3zr'])
        self.fields['uzr'].SetValue(v['uzr'])
        self.fields['xzr'].SetValue(v['xzr'])
        self.fields['o3_h'].SetValue(v['o3_h'])
        self.fields['u_h'].SetValue(v['u_h'])
        self.fields['o3_h_copy'].SetValue(v['o3_h_copy'])
        self.fields['u_h_copy'].SetValue(v['u_h_copy'])
        self.fields['soil_tex'].SetStringSelection(
            {-4.0: 'Coarse', -5.5: 'Medium', -7.0: 'Fine'}[v['soil_a']]
        )
        self.fields['rsoil'].SetValue(v['rsoil'])
        self.fields['o3_h'].Enable(not self.fields['o3_h_copy'].IsChecked())
        self.fields['u_h'].Enable(not self.fields['u_h_copy'].IsChecked())
