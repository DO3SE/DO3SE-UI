import wx

from .. import wxext
from ..FloatSpin import FloatSpin
from ..app import logging, app

class VegParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.fields = dict()

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)
        self.presets = wxext.PresetChooser(self)
        self.presets.SetPresets(app.config['preset.veg'])
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues
        def f():
            app.config['preset.veg'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f
        s.Add(self.presets, 0, wx.ALL|wx.EXPAND, 6)
        sVegParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sVegParams.AddGrowableCol(0)
        sVegParams.AddGrowableCol(1)
        s.Add(sVegParams, 0, wx.ALL|wx.EXPAND, 6)

        # Characteristics
        sChar = wxext.StaticBox2Col(self, "Characteristics")
        sVegParams.Add(sChar, 0, wx.EXPAND)
        sChar.fgs.Add(wx.StaticText(self, label="Canopy height (m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['h'] = wx.SpinCtrl(self, min=1, max=100, initial=25)
        sChar.fgs.Add(self.fields['h'], 0)
        sChar.fgs.Add(wx.StaticText(self, label="Root depth (m)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['root'] = FloatSpin(self, value=1.2, min_val=0.01, 
                increment=0.1, digits=1)
        sChar.fgs.Add(self.fields['root'], 0)
        sChar.fgs.Add(wx.StaticText(self, label="Min. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lai_min'] = FloatSpin(self, value=0.0, min_val=0,
                increment=0.1, digits=1)
        sChar.fgs.Add(self.fields['lai_min'], 0)
        sChar.fgs.Add(wx.StaticText(self, label="Max. Leaf Area Index (m^2/m^2)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['lai_max'] = FloatSpin(self, value=4.0, min_val=0,
                increment=0.1, digits=1)
        sChar.fgs.Add(self.fields['lai_max'], 0)

        # Growing season
        sSeason = wxext.StaticBox2Col(self, "Growing season")
        sVegParams.Add(sSeason, 0, wx.EXPAND)
        sSeason.fgs.Add(wx.StaticText(self, label="Start (day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['sgs'] = wx.SpinCtrl(self, min=1, max=365, initial=121)
        sSeason.fgs.Add(self.fields['sgs'])
        sSeason.fgs.Add(wx.StaticText(self, label="End (day of year)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['egs'] = wx.SpinCtrl(self, min=1, max=365, initial=273)
        sSeason.fgs.Add(self.fields['egs'])
        sSeason.fgs.Add(wx.StaticText(self, label="Start - upper leaf"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['astart'] = wx.SpinCtrl(self, min=1, max=365, initial=121)
        sSeason.fgs.Add(self.fields['astart'])
        sSeason.fgs.Add(wx.StaticText(self, label="End - upper leaf"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['aend'] = wx.SpinCtrl(self, min=1, max=365, initial=273)
        sSeason.fgs.Add(self.fields['aend'])

        # Maintain integrity on growing season
        def f(evt):
            if self.fields['sgs'].GetValue() > self.fields['egs'].GetValue():
                self.fields['sgs'].SetValue(self.fields['egs'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['sgs'])
        def f(evt):
            if self.fields['egs'].GetValue() < self.fields['sgs'].GetValue():
                self.fields['egs'].SetValue(self.fields['sgs'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['egs'])
        def f(evt):
            if self.fields['astart'].GetValue() > self.fields['aend'].GetValue():
                self.fields['astart'].SetValue(self.fields['aend'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['astart'])
        def f(evt):
            if self.fields['aend'].GetValue() < self.fields['astart'].GetValue():
                self.fields['aend'].SetValue(self.fields['astart'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['aend'])

        # Environmental dependence
        sGrowth = wxext.StaticBox2Col(self, "Environmental dependence")
        sVegParams.Add(sGrowth, 0, wx.EXPAND)
        sGrowth.fgs.Add(wx.StaticText(self, label="Minimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_min'] = wx.SpinCtrl(self, min=-10, max=100, initial=0)
        sGrowth.fgs.Add(self.fields['t_min'], 0)
        sGrowth.fgs.Add(wx.StaticText(self, label="Optimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_opt'] = wx.SpinCtrl(self, min=-10, max=100, initial=21)
        sGrowth.fgs.Add(self.fields['t_opt'])
        sGrowth.fgs.Add(wx.StaticText(self, label="Maximum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_max'] = wx.SpinCtrl(self, min=-10, max=100, initial=35)
        sGrowth.fgs.Add(self.fields['t_max'], 0)
        # TODO: min/max values for VPD
        sGrowth.fgs.Add(wx.StaticText(self, label="VPD for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['vpd_min'] = FloatSpin(self, value=3.25, increment=0.01, digits=2)
        sGrowth.fgs.Add(self.fields['vpd_min'], 0)
        sGrowth.fgs.Add(wx.StaticText(self, label="VPD for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['vpd_max'] = FloatSpin(self, value=1.0, increment=0.01, digits=2)
        sGrowth.fgs.Add(self.fields['vpd_max'], 0)
        # TODO: min/max for SWP
        sGrowth.fgs.Add(wx.StaticText(self, label="SWP for minimum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['swp_min'] = FloatSpin(self, value=-1.25, increment=0.01, digits=2)
        sGrowth.fgs.Add(self.fields['swp_min'], 0)
        sGrowth.fgs.Add(wx.StaticText(self, label="SWP for maximum growth"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['swp_max'] = FloatSpin(self, value=-0.5, increment=0.01, digits=2)
        sGrowth.fgs.Add(self.fields['swp_max'], 0)

        # Maintain integrity on environmental dependence
        def f(evt):
            if self.fields['t_opt'].GetValue() < self.fields['t_min'].GetValue():
                self.fields['t_opt'].SetValue(self.fields['t_min'].GetValue())
            elif self.fields['t_opt'].GetValue() > self.fields['t_max'].GetValue():
                self.fields['t_opt'].SetValue(self.fields['t_max'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_opt'])
        def f(evt):
            if self.fields['t_min'].GetValue() > self.fields['t_opt'].GetValue():
                self.fields['t_min'].SetValue(self.fields['t_opt'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_min'])
        def f(evt):
            if self.fields['t_max'].GetValue() < self.fields['t_opt'].GetValue():
                self.fields['t_max'].SetValue(self.fields['t_opt'].GetValue())
        self.Bind(wx.EVT_SPINCTRL, f, self.fields['t_max'])

    def getvalues(self):
        return { 
            'h':        float(self.fields['h'].GetValue()),
            'root':     float(self.fields['root'].GetValue()),
            'lai_min':  float(self.fields['lai_min'].GetValue()),
            'lai_max':  float(self.fields['lai_max'].GetValue()),
            't_min':    float(self.fields['t_min'].GetValue()),
            't_opt':    float(self.fields['t_opt'].GetValue()),
            't_max':    float(self.fields['t_max'].GetValue()),
            'vpd_min':  float(self.fields['vpd_min'].GetValue()),
            'vpd_max':  float(self.fields['vpd_max'].GetValue()),
            'swp_min':  float(self.fields['swp_min'].GetValue()),
            'swp_max':  float(self.fields['swp_max'].GetValue()),
            'sgs':      float(self.fields['sgs'].GetValue()),
            'egs':      float(self.fields['egs'].GetValue()),
            'astart':   float(self.fields['astart'].GetValue()),
            'aend':     float(self.fields['aend'].GetValue()),
        }

    def setvalues(self, v):
        self.fields['h'].SetValue(v['h'])
        self.fields['root'].SetValue(v['root'])
        self.fields['lai_min'].SetValue(v['lai_min'])
        self.fields['lai_max'].SetValue(v['lai_max'])
        self.fields['t_min'].SetValue(v['t_min'])
        self.fields['t_opt'].SetValue(v['t_opt'])
        self.fields['t_max'].SetValue(v['t_max'])
        self.fields['vpd_min'].SetValue(v['vpd_min'])
        self.fields['vpd_max'].SetValue(v['vpd_max'])
        self.fields['swp_min'].SetValue(v['swp_min'])
        self.fields['swp_max'].SetValue(v['swp_max'])
        self.fields['sgs'].SetValue(v['sgs'])
        self.fields['egs'].SetValue(v['egs'])
        self.fields['astart'].SetValue(v['astart'])
        self.fields['aend'].SetValue(v['aend'])
