import wx

import wxext
import model

class SavePanel(wx.Panel):
    def __init__(self, app, parent, dataset, startdir):
        wx.Panel.__init__(self, parent)

        self.dataset = dataset
        self.prevdir = startdir

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.EXPAND|wx.ALL, 6)
        self.presets.SetPresets(app.config['output_format'])
        # Force a sync of the config on a preset change
        def f():
            app.config['output_format'] = self.presets.GetPresets()
            app.config.sync()
        self.presets.post_update = f

        # List selector
        self.slOutputs = wxext.ListSelectCtrl(self)
        s.Add(self.slOutputs, 1, wx.EXPAND|wx.ALL, 6)
        self.slOutputs.SetAvailable([(x['long'], x['variable']) for x in model.output_fields])
        
        # "Include column headers?"
        sHeaders = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sHeaders, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        self.chkOutputHeaders = wx.CheckBox(self, label="Include column headers")
        sHeaders.Add(self.chkOutputHeaders, 0, wx.EXPAND)
        self.chkOutputHeaders.SetValue(True)

        # "Save" button
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bSave = wx.Button(self, wx.ID_SAVEAS)
        sButtons.Add(bSave, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_save, bSave)
        
        # Preset manager get-/setvalues callbacks
        def f():
            return {
                'fields': self.GetFields(),
                'headers': self.GetAddHeaders()
            }
        self.presets.getvalues = f
        def f(v):
            self.slOutputs.SetSelection((model.output_field_map[x]['long'] for x in v['fields']))
            self.chkOutputHeaders.SetValue(v['headers'])
        self.presets.setvalues = f

    
    def GetFields(self):
        return [b for a,b in self.slOutputs.GetSelectionWithData()]

    
    def GetAddHeaders(self):
        return self.chkOutputHeaders.GetValue()


    def _on_save(self, evt):
        fd = wx.FileDialog(self, message = 'Save results',
                defaultDir = self.prevdir,
                wildcard = 'Comma-separated values (*.csv)|*.csv|All files (*.*)|*',
                style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            self.prevdir = fd.GetDirectory()
            path = fd.GetPath()
            if not path.split('.')[-1] == 'csv': path = path + '.csv'
            self.dataset.save(path, self.GetFields(), headers=self.GetAddHeaders())
            wx.MessageDialog(self, message = 'Results saved!',
                    style = wx.OK|wx.ICON_INFORMATION)
