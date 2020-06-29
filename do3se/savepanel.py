import wx

import wxext
import model
import dialogs

class SavePanel(wx.Panel):
    def __init__(self, app, parent, results):
        wx.Panel.__init__(self, parent)

        self.app = app
        self.results = results

        # Outer sizer
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        # Preset manager
        self.presets = wxext.PresetChooser(self)
        s.Add(self.presets, 0, wx.EXPAND|wx.ALL, 5)
        self.presets.SetPresets(app.config.data['output_formats'])
        # Force a sync of the config on a preset change
        def f():
            app.config.data['output_formats'] = self.presets.GetPresets()
            app.config.save()
        self.presets.post_update = f

        # List selector
        self.slOutputs = wxext.SaveListSelectCtrl(self)
        s.Add(self.slOutputs, 1, wx.EXPAND|wx.ALL, 5)
        self.slOutputs.SetAvailable([(x['long'], x['variable']) for x in model.output_fields.values()])

        # "Include column headers?"
        sHeaders = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sHeaders, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        self.chkOutputHeaders = wx.CheckBox(self, label="Include column headers")
        sHeaders.Add(self.chkOutputHeaders, 0, wx.EXPAND)
        self.chkOutputHeaders.SetValue(True)

        self.chkReduceOutput = wx.CheckBox(self, label="Only data from during growing season")
        sHeaders.Add(self.chkReduceOutput, 0, wx.EXPAND|wx.LEFT, 10)

        # "Save" button
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        bSave = wx.Button(self, wx.ID_SAVEAS)
        sButtons.Add(bSave, 0, wx.EXPAND|wx.LEFT, 5)
        self.Bind(wx.EVT_BUTTON, self._on_save, bSave)

        self.presets.getvalues = self.get_values
        self.presets.setvalues = self.set_values


    def get_values(self):
        return {'fields': self.GetFields(),
                'headers': self.chkOutputHeaders.GetValue(),
                'reduce': self.chkReduceOutput.GetValue()}


    def set_values(self, values):
        self.slOutputs.SetSelection((model.output_fields[f]['long'] for f in values['fields']))
        self.chkOutputHeaders.SetValue(values['headers'])
        self.chkReduceOutput.SetValue(values['reduce'])


    def GetFields(self):
        return [b for a,b in self.slOutputs.GetSelectionWithData()]


    def GetAddHeaders(self):
        return self.chkOutputHeaders.GetValue()


    def GetDateRange(self):
        if self.chkReduceOutput.GetValue():
            return (self.results.params['sgs'], self.results.params['egs'])
        else:
            return None


    def _on_save(self, evt):
        filename = dialogs.save_datafile(self)

        if filename is not None:
            self.results.save(open(filename, 'wb'),
                              self.GetFields(),
                              self.GetAddHeaders(),
                              self.GetDateRange())
