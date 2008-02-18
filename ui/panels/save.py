import wx

from .. import wxext
from .. import maps
from ..FloatSpin import FloatSpin
from ..app import logging, app

class Save(wx.Panel):
    def __init__(self, parent, dataset, startdir):
        wx.Panel.__init__(self, parent)

        self.dataset = dataset
        self.prevdir = startdir

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

        # "Save" button
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bSave = wx.Button(self, wx.ID_SAVEAS)
        sButtons.Add(bSave, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_save, bSave)
        
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

    
    def GetFields(self):
        return maps.outputs.rmap(self.slOutputs.GetSelection())

    
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
            self.dataset.save(path, maps.outputs.rmap(self.slOutputs.GetSelection()), 
                    headers=self.chkOutputHeaders.GetValue)
            wx.MessageDialog(self, message = 'Results saved!',
                    style = wx.OK|wx.ICON_INFORMATION)
