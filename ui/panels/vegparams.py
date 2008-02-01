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
        #self.presets.getvalues = self.get_veg_params
        #self.presets.setvalues = self.set_veg_params
        def f():
            app.config['preset.veg'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f
        s.Add(self.presets, 0, wx.ALL|wx.EXPAND, 6)
        sVegParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sVegParams.AddGrowableCol(0)
        sVegParams.AddGrowableCol(1)
        s.Add(sVegParams, 0, wx.ALL|wx.EXPAND, 6)

        # Growth parameters
        sGrowth = wxext.StaticBox2Col(self, "Growth parameters")
        sVegParams.Add(sGrowth, 0, wx.EXPAND)
        sGrowth.fgs.Add(wx.StaticText(self, label="Minimum temperature (Celcius)"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.fields['t_min'] = wx.SpinCtrl(self, min=-10, max=100, initial=0)
        sGrowth.fgs.Add(self.fields['t_min'], 0)
