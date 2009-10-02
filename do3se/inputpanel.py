import wx

import wxext
import model

class InputPanel(wx.Panel):
    def __init__(self, app, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.EXPAND|wx.ALL, 6)
        self.presets.SetPresets(app.config['input_format'])
        # Force a sync of the config on a preset change
        def f():
            app.config['input_format'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f

        # List selector
        self.lsInputs = wxext.ListSelectCtrl(self)
        s.Add(self.lsInputs, 1, wx.EXPAND|wx.ALL, 6)
        self.lsInputs.SetAvailable([(x['long'], x['variable']) for x in model.input_fields])
        
        # Header trim
        sTrim = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sTrim, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        sTrim.Add(wx.StaticText(self, \
            label='Number of lines to trim from beginning of file (e.g. for column headers)'),
            0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 6)
        self.spinInputTrim = wx.SpinCtrl(self, min=0, max=10, initial=0, style=wx.SP_ARROW_KEYS)
        sTrim.Add(self.spinInputTrim, 0, wx.EXPAND)
        
        # Preset manager get-/setvalues callbacks
        self.presets.getvalues = self.getvalues
        self.presets.setvalues = self.setvalues

    def getvalues(self):
        return {
                'fields': self.GetFields(),
                'trim': self.GetTrim(),
        }

    def setvalues(self, v):
        self.lsInputs.SetSelection((model.input_field_map[x]['long'] for x in v['fields']))
        self.spinInputTrim.SetValue(v['trim'])

    def GetFields(self):
        return [b for a,b in self.lsInputs.GetSelectionWithData()]

    def GetTrim(self):
        return int(self.spinInputTrim.GetValue())
