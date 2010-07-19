import wx

import wxext
import model
from util.fieldgroup import FieldGroup, Field, wxField

class SavePanel(wx.Panel):
    def __init__(self, app, parent, dataset, startdir):
        wx.Panel.__init__(self, parent)

        self.app = app

        self.dataset = dataset
        self.prevdir = startdir

        self.fields = FieldGroup()

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

        self.chkReduceOutput = wx.CheckBox(self, label="Only data from during growing season")
        sHeaders.Add(self.chkReduceOutput, 0, wx.EXPAND|wx.LEFT, 12)

        # "Save" button
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bSave = wx.Button(self, wx.ID_SAVEAS)
        sButtons.Add(bSave, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_save, bSave)

        # Setup FieldGroup
        self.fields.add('fields', Field(self.slOutputs,
            lambda : [b for a,b in self.slOutputs.GetSelectionWithData()],
            lambda fields: self.slOutputs.SetSelection((model.output_field_map[f]['long'] for f in fields))))
        self.fields.add('headers', wxField(self.chkOutputHeaders))
        self.fields.add('reduce', wxField(self.chkReduceOutput))

        self.presets.getvalues = self.fields.get_values
        self.presets.setvalues = self.fields.set_values

    
    def GetFields(self):
        return [b for a,b in self.slOutputs.GetSelectionWithData()]

    
    def GetAddHeaders(self):
        return self.chkOutputHeaders.GetValue()


    def GetDateRange(self):
        if self.chkReduceOutput.GetValue():
            return (self.dataset.vegparams['sgs'], self.dataset.vegparams['egs'])
        else:
            return None


    def _on_save(self, evt):
        fd = wx.FileDialog(self, message = 'Save results',
                defaultDir = self.prevdir,
                wildcard = 'Comma-separated values (*.csv)|*.csv|All files (*.*)|*',
                style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            self.prevdir = fd.GetDirectory()
            path = fd.GetPath()
            if not path.split('.')[-1] == 'csv':
                path = path + '.csv'

            try:
                outfile = open(path, 'wb')
            except IOError:
                wx.MessageBox('Failed to write results to file "' + path + '"',
                              self.app.title, wx.OK|wx.ICON_ERROR, self)
                return

            self.dataset.save(outfile, self.GetFields(), 
                              headers=self.GetAddHeaders(),
                              period=self.GetDateRange())
            outfile.close()
            wx.MessageDialog(self, message = 'Results saved!',
                    style = wx.OK|wx.ICON_INFORMATION)
