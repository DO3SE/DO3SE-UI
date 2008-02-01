import wx

from .. import wxext
from .. import maps
from ..FloatSpin import FloatSpin
from ..app import logging, app

class OutputParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.EXPAND|wx.ALL, 6)
        self.presets.SetPresets(app.config['preset.outputs'])
        # Force a sync of the config on a preset change
        def f():
            app.config['preset.outputs'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f

        # List selector
        self.slOutputs = wxext.ListSelectCtrl(self)
        s.Add(self.slOutputs, 1, wx.EXPAND|wx.ALL, 6)
        self.slOutputs.SetAvailable(maps.outputs.values())
        
        # "Include column headers?"
        sHeaders = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sHeaders, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        self.chkOutputHeaders = wx.CheckBox(self, label="Include column headers")
        sHeaders.Add(self.chkOutputHeaders, 0, wx.EXPAND)
        self.chkOutputHeaders.SetValue(True)
        
        # Preset manager get-/setvalues callbacks
        def f():
            return {
                'fields': maps.outputs.rmap(self.slOutputs.GetSelection()),
                'headers': self.chkOutputHeaders.GetValue()
            }
        self.presets.getvalues = f
        def f(v):
            self.slOutputs.SetSelection(maps.outputs.map(v['fields']))
            self.chkOutputHeaders.SetValue(v['headers'])
        self.presets.setvalues = f
