import wx

from .. import wxext
from .. import maps
from ..FloatSpin import FloatSpin
from ..app import logging, app

class InputParams(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.EXPAND|wx.ALL, 6)
        self.presets.SetPresets(app.config['preset.inputs'])
        # Force a sync of the config on a preset change
        def f():
            app.config['preset.inputs'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f

        # List selector
        self.lsInputs = wxext.ListSelectCtrl(self)
        s.Add(self.lsInputs, 1, wx.EXPAND|wx.ALL, 6)
        self.lsInputs.SetAvailable(maps.inputs.values())
        
        # Header trim
        sTrim = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sTrim, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        sTrim.Add(wx.StaticText(self, \
            label='Number of lines to trim from beginning of file (e.g. for column headers)'),
            0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 6)
        self.spinInputTrim = wx.SpinCtrl(self, min=0, max=10, initial=0, style=wx.SP_ARROW_KEYS)
        sTrim.Add(self.spinInputTrim, 0, wx.EXPAND)
        
        # Preset manager get-/setvalues callbacks
        def f():
            return {
                'fields': maps.inputs.rmap(self.lsInputs.GetSelection()),
                'trim': self.spinInputTrim.GetValue(),
            }
        self.presets.getvalues = f
        def f(v):
            self.lsInputs.SetSelection(maps.inputs.map(v['fields']))
            self.spinInputTrim.SetValue(v['trim'])
        self.presets.setvalues = f
