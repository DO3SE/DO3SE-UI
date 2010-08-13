import wx
from wx.lib import scrolledpanel
from wx.lib.fancytext import StaticFancyText

import wxext
import model
from util.fieldgroup import Field, FieldGroup, wxField, wxFloatField

class SoilTexField(Field):
    """
    Custom field for creating the Soil Texture selector and implementing the
    getter/setter logic.
    """
    def __init__(self, parent):
        obj = wx.Choice(parent)
        for x in model.soil_classes:
            obj.Append(x['name'], x['id'])
        Field.__init__(self, obj)

    def get(self):
        return self.obj.GetClientData(self.obj.GetSelection())

    def set(self, value):
        self.obj.SetStringSelection(model.soil_class_map[value]['name'])



class SitePanel(wx.Panel):
    def __init__(self, app, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Dict to contain the actual input controls
        self.fields = FieldGroup()

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

        p = scrolledpanel.ScrolledPanel(self)
        s.Add(p, 1, wx.EXPAND)
        s = wx.BoxSizer(wx.VERTICAL)
        p.SetSizer(s)

        
        # FlexGridSizer for the sections
        sSiteParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sSiteParams.AddGrowableCol(0)
        sSiteParams.AddGrowableCol(1)
        s.Add(sSiteParams, 0, wx.ALL|wx.EXPAND, 6)
        
        # Location parameters
        sLocation = wxext.StaticBox2Col(p, "Site location")
        sSiteParams.Add(sLocation, 0, wx.EXPAND)

        # XXX: DONE
        sLocation.fgs.Add(wx.StaticText(p, label="Latitude"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lat', wxFloatField(wxext.FloatSpin(p,
            value=50.0, min_val=-90.0, max_val=90.0, increment=0.1, digits=3)))
        sLocation.fgs.Add(self.fields['lat'].obj, 0)

        # XXX: DONE
        sLocation.fgs.Add(wx.StaticText(p, label="Longitude"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('lon', wxFloatField(wxext.FloatSpin(p,
            value=0.0, min_val=-180.0, max_val=180.0, increment=0.1, digits=3)))
        sLocation.fgs.Add(self.fields['lon'].obj, 0)

        # XXX: DONE
        sLocation.fgs.Add(wx.StaticText(p, label="Elevation (metres above sea level)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('elev', wxFloatField(wx.SpinCtrl(p,
            min=-100, max=5000, initial=0)))
        sLocation.fgs.Add(self.fields['elev'].obj, 0)


        # Measurement heights
        sHeights = wxext.StaticBox2Col(p, "Measurement heights")
        sSiteParams.Add(sHeights, 0, wx.EXPAND)

        # XXX: DONE
        sHeights.fgs.Add(StaticFancyText(p, -1, "Ozone concentration data (h<sub>O</sub>, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('o3zr', wxFloatField(wx.SpinCtrl(p,
            min=1, max=200, initial=25)))
        sHeights.fgs.Add(self.fields['o3zr'].obj, 0)

        # XXX: DONE
        sHeights.fgs.Add(StaticFancyText(p, -1, "Wind speed data (h<sub>w</sub>, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('uzr', wxFloatField(wx.SpinCtrl(p,
            min=1, max=200, initial=25)))
        sHeights.fgs.Add(self.fields['uzr'].obj, 0)
        # XXX: DONE
        sHeights.fgs.Add(StaticFancyText(p, -1, "Soil water measurement depth (D<sub>meas</sub>, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('d_meas', wxFloatField(wxext.FloatSpin(p,
            value=0.5, min_val=0.1, max_val=2.0, increment=0.1, digits=1)))
        sHeights.fgs.Add(self.fields['d_meas'].obj, 0)


        # Soil properties
        sSoil = wxext.StaticBox2Col(p, "Soil")
        sSiteParams.Add(sSoil, 0, wx.EXPAND)

        sSoil.fgs.Add(wx.StaticText(p, label="Texture"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('soil_tex', SoilTexField(p))
        self.fields['soil_tex'].set(model.default_soil_class)
        sSoil.fgs.Add(self.fields['soil_tex'].obj, 0)

        sSoil.fgs.Add(wx.StaticText(p, label="Rsoil"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields.add('rsoil', wxFloatField(wx.SpinCtrl(p,
            min=1, max=1000, initial=200)))
        sSoil.fgs.Add(self.fields['rsoil'].obj, 0)

        # Canopy heights
        sCanopies = wxext.StaticBox2Col(p, "Reference canopy heights")
        sSiteParams.Add(sCanopies, 0, wx.EXPAND)

        sCanopies.fgs.Add(StaticFancyText(p, -1, "Ozone concentration data (h<sub>ref,O</sub>, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteO3Canopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteO3Canopy, 0)
        self.fields.add('o3_h', wxFloatField(wx.SpinCtrl(p,
            min=1, max=200, initial=25)))
        sSiteO3Canopy.Add(self.fields['o3_h'].obj, 0, wx.RIGHT, 6)
        self.fields.add('o3_h_copy', wxField(wx.CheckBox(p,
            label="Same as target canopy")))
        sSiteO3Canopy.Add(self.fields['o3_h_copy'].obj, 0)
        self.fields['o3_h_copy'].Bind(wx.EVT_CHECKBOX, self.On_o3_h_copy_EVT_CHECKBOX)

        sCanopies.fgs.Add(StaticFancyText(p, -1, "Wind speed data (h<sub>ref,w</sub>, m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteMetCanopy = wx.BoxSizer(wx.HORIZONTAL)
        sCanopies.fgs.Add(sSiteMetCanopy, 0)
        self.fields.add('u_h', wxFloatField(wx.SpinCtrl(p,
            min=1, max=200, initial=25)))
        sSiteMetCanopy.Add(self.fields['u_h'].obj, 0, wx.RIGHT, 6)
        self.fields.add('u_h_copy', wxField(wx.CheckBox(p,
            label="Same as target canopy")))
        sSiteMetCanopy.Add(self.fields['u_h_copy'].obj, 0)
        self.fields['u_h_copy'].Bind(wx.EVT_CHECKBOX, self.On_u_h_copy_EVT_CHECKBOX)

        tfpng = wxext.PNGPanel(p, 'resources/transfer.png')
        s.Add(tfpng, 0, wx.ALL, 6)


        p.SetupScrolling()


    def On_o3_h_copy_EVT_CHECKBOX(self, evt):
        self.fields['o3_h'].Enable(not self.fields['o3_h_copy'].IsChecked())


    def On_u_h_copy_EVT_CHECKBOX(self, evt):
        self.fields['u_h'].Enable(not self.fields['u_h_copy'].IsChecked())


    def getvalues(self):
        return self.fields.get_values()


    def setvalues(self, v):
        # Set the values
        self.fields.set_values(v)

        # Fire off related events to make the UI consistent
        self.On_o3_h_copy_EVT_CHECKBOX(None)
        self.On_u_h_copy_EVT_CHECKBOX(None)
