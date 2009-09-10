import wx

from .. import wxext
from .. import dose
from ..FloatSpin import FloatSpin
from ..app import logging, app
from ..fieldgroup import Field, FieldGroup

class SiteParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Dict to contain the actual input controls
        self.fields = dict()

        self.fieldgroup = FieldGroup()

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.ALL|wx.EXPAND, 6)
        self.presets.SetPresets(app.config['site_params'])
        # Get/set callbacks
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues
        # Force a sync of the config on a preset change
        def f():
            app.config['site_params'] = self.presets.GetPresets()
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
        self.fieldgroup.add_field('lat', Field(
                lambda : float(self.fields['lat'].GetValue()),
                self.fields['lat'].SetValue))

        sLocation.fgs.Add(wx.StaticText(self, label="Longitude"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lon'] = FloatSpin(self, value=0.0,
                min_val=-180.0, max_val=180.0, increment=0.1, digits=3)
        sLocation.fgs.Add(self.fields['lon'], 0)
        self.fieldgroup.add_field('lon', Field(
                lambda : float(self.fields['lon'].GetValue()),
                self.fields['lon'].SetValue))

        sLocation.fgs.Add(wx.StaticText(self, label="Elevation"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['elev'] = wx.SpinCtrl(self, min=-100, max=5000, initial=0)
        sLocation.fgs.Add(self.fields['elev'], 0)
        self.fieldgroup.add_field('elev', Field(
                lambda : float(self.fields['elev'].GetValue()),
                self.fields['elev'].SetValue))


        # Measurement heights
        sHeights = wxext.StaticBox2Col(self, "Measurement heights")
        sSiteParams.Add(sHeights, 0, wx.EXPAND)

        sHeights.fgs.Add(wx.StaticText(self, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['o3zr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['o3zr'], 0)
        self.fieldgroup.add_field('o3zr', Field(
                lambda : float(self.fields['o3zr'].GetValue()),
                self.fields['o3zr'].SetValue))

        sHeights.fgs.Add(wx.StaticText(self, label="Meteorological data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['uzr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['uzr'], 0)
        self.fieldgroup.add_field('uzr', Field(
                lambda : float(self.fields['uzr'].GetValue()),
                self.fields['uzr'].SetValue))

        sHeights.fgs.Add(wx.StaticText(self, label="Other data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['xzr'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sHeights.fgs.Add(self.fields['xzr'], 0)
        self.fieldgroup.add_field('xzr', Field(
                lambda : float(self.fields['xzr'].GetValue()),
                self.fields['xzr'].SetValue))


        # Soil properties
        sSoil = wxext.StaticBox2Col(self, "Soil")
        sSiteParams.Add(sSoil, 0, wx.EXPAND)

        sSoil.fgs.Add(wx.StaticText(self, label="Texture"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['soil_tex'] = wx.Choice(self)
        for x in dose.soil_classes:
            self.fields['soil_tex'].Append(x['name'], x['id'])
        self.fields['soil_tex'].SetStringSelection(
                dose.soil_class_map[dose.default_soil_class]['name'])
        sSoil.fgs.Add(self.fields['soil_tex'], 0)
        self.fieldgroup.add_field('soil_tex', Field(
                lambda : self.fields['soil_tex'].GetClientData(self.fields['soil_tex'].GetSelection()),
                lambda x: self.fields['soil_tex'].SetStringSelection(dose.soil_class_map[x]['name'])))

        sSoil.fgs.Add(wx.StaticText(self, label="Rsoil"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['rsoil'] = wx.SpinCtrl(self, min=1, max=1000, initial=200)
        sSoil.fgs.Add(self.fields['rsoil'], 0)
        self.fieldgroup.add_field('rsoil', Field(
                lambda : float(self.fields['rsoil'].GetValue()),
                self.fields['rsoil'].SetValue))

        # Canopy heights
        sCanopies = wxext.StaticBox2Col(self, "Canopy heights")
        sSiteParams.Add(sCanopies, 0, wx.EXPAND)

        sCanopies.fgs.Add(wx.StaticText(self, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteO3Canopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteO3Canopy, 0)
        self.fields['o3_h'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sSiteO3Canopy.Add(self.fields['o3_h'], 0, wx.RIGHT, 6)
        self.fieldgroup.add_field('o3_h', Field(
                lambda : float(self.fields['o3_h'].GetValue()),
                self.fields['o3_h'].SetValue))
        self.fields['o3_h_copy'] = wx.CheckBox(self, label="Same as target canopy")
        sSiteO3Canopy.Add(self.fields['o3_h_copy'], 0)
        self.fields['o3_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.fields['o3_h'].Enable(not self.fields['o3_h_copy'].IsChecked()),
                self.fields['o3_h_copy'])
        def f(x):
             self.fields['o3_h_copy'].SetValue(x)
             self.fields['o3_h'].Enable(not self.fields['o3_h_copy'].IsChecked())
        self.fieldgroup.add_field('o3_h_copy', Field(
                self.fields['o3_h_copy'].GetValue, f))

        sCanopies.fgs.Add(wx.StaticText(self, label="Meteorological data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteMetCanopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteMetCanopy, 0)
        self.fields['u_h'] = wx.SpinCtrl(self, min=1, max=200, initial=25)
        sSiteMetCanopy.Add(self.fields['u_h'], 0, wx.RIGHT, 6)
        self.fieldgroup.add_field('u_h', Field(
                lambda : float(self.fields['u_h'].GetValue()),
                self.fields['u_h'].SetValue))
        self.fields['u_h_copy'] = wx.CheckBox(self, label="Same as target canopy")
        sSiteMetCanopy.Add(self.fields['u_h_copy'], 0)
        self.fields['u_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.fields['u_h'].Enable(not self.fields['u_h_copy'].IsChecked()),
                self.fields['u_h_copy'])
        def f(x):
             self.fields['u_h_copy'].SetValue(x)
             self.fields['u_h'].Enable(not self.fields['u_h_copy'].IsChecked())
        self.fieldgroup.add_field('u_h_copy', Field(
                self.fields['u_h_copy'].GetValue, f))


    def getvalues(self):
        return self.fieldgroup.get_values()


    def setvalues(self, v):
        return self.fieldgroup.set_values(v)
