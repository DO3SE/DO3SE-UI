import wx

class PresetChooser(wx.Panel):
    """Preset manager widget

    A simple generic preset manager widget with save and delete buttons.  A few
    things must be set externally to make this work:

        getvalues()     - A procedure to get the values from whatever is being 
                          managed by the PresetChooser
        setvalues(v)    - A procedure to load the values from the current preset 
                          into the managed entity

    Optionally, the following can also be overridden to add extra functionality:

        post_save()     - Called after saving a preset - ideal for some kind of 
                          saving of configuration to a file

    Typical usage might look like:
        
        import wxext
        foo = wxext.PresetChooser(self)
        foo.getvalues = self.GetValues
        foo.setvalues = self.SetValues
        foo.post_save = lambda: config['foo'] = foo.GetPresets()
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        self.choice = wx.Choice(self)
        sizer.Add(wx.StaticText(self, label = 'Presets:'), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 4)
        sizer.Add(self.choice, 1, wx.EXPAND)

        self.button_save = wx.Button(self, wx.ID_SAVE, style = wx.BU_EXACTFIT)
        sizer.Add(self.button_save, 0, wx.EXPAND | wx.LEFT, 4)
        self.button_delete = wx.Button(self, wx.ID_DELETE, style = wx.BU_EXACTFIT)
        sizer.Add(self.button_delete, 0, wx.EXPAND | wx.LEFT, 4)

        # Bindings
        self.Bind(wx.EVT_CHOICE, self.OnChange, self.choice)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.button_save)
        self.Bind(wx.EVT_BUTTON, self.OnDelete, self.button_delete)


    def SetPresets(self, presets, blacklist=[]):
        self.presets = presets.copy()
        self.blacklist = blacklist
        self.choice.Clear()
        self.choice.SetItems(list(self.presets.keys()))

    
    def GetPresets(self):
        return self.presets


    def Refresh(self):
        key = self.choice.GetStringSelection()
        self.choice.Clear()
        self.choice.SetItems(list(self.presets.keys()))
        if key and key in self.presets:
            self.choice.SetStringSelection(key)
            self.setvalues(self.presets[key])


    def OnChange(self, evt):
        self.setvalues(self.presets[self.choice.GetStringSelection()])


    def OnSave(self, evt):
        item = self.getvalues()
        key = wx.GetTextFromUser("Save preset as:", "DO3SE", self.choice.GetStringSelection(), self)

        if key:
            if key in self.blacklist:
                wx.MessageBox("This preset name is reserved, please use another", 'DO3SE',
                        wx.OK|wx.ICON_ERROR, self)
            elif (not key in self.presets or \
                    wx.MessageBox("Overwrite existing preset '%s'?" % (key), 'DO3SE',
                        wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT, self) == wx.YES):
                self.presets[key] = item
                self.Refresh()
                self.choice.SetStringSelection(key)
                self.setvalues(self.presets[key])
                self.post_update()

    
    def OnDelete(self, evt):
        key = self.choice.GetStringSelection()

        if key and wx.MessageBox("Delete preset '%s'?" % (key), 'DO3SE', 
                wx.YES_NO | wx.ICON_WARNING, self) == wx.YES:
            del self.presets[key]
            self.Refresh()
            self.post_update()


    def getvalues(self):
        pass


    def setvalues(self, v):
        pass

    def post_update(self):
        pass
