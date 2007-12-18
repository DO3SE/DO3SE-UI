###############################################################################
# wxext.py - wxPython extensions
# (c)2007 Alan Briolat
#
# A collection of extra wxPython widgets usable via XRC subclassing
###############################################################################

import wx
from tools import _verbose

class FloatCtrl(wx.TextCtrl):
    """Range-checked floating-point input control."""

    def __init__(self):
        p = wx.PreTextCtrl()
        self.PostCreate(p)

        self.default = 0.0
        self.min = None
        self.max = None

        self.Bind(wx.EVT_TEXT, self.OnChange)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        self.SetValue(str(self.default))

    def OnChange(self, evt):
        """Validate input value whenever it changes.

        Check that the input value can be converted to a floating-point number
        and that it's within range if a range is specified.
        """
        if not self.GetValue():
            self.floatvalue = self.default
        else:
            try:
                # Try to turn the input string into a floating-point value
                self.floatvalue = float(self.GetValue())

                # --- This stuff only happend on success ---
                # Check if the value is in range if a range is set
                if ((not self.min is None) and (self.floatvalue < self.min)) \
                        or ((not self.max is None) and (self.floatvalue > self.max)):
                    self.OnValidationFailed()
                else:
                    self.OnValidationSuccess()
            except ValueError:
                self.OnValidationFailed()
    
    def OnKillFocus(self, evt):
        """Range check value and update display.

        If a range has been set, clip the value to be within that range and then
        update the display to match the most recent valid value.
        """
        if not self.min is None:
            self.floatvalue = max(self.min, self.floatvalue)
        if not self.max is None:
            self.floatvalue = min(self.max, self.floatvalue)
        self.ChangeValue(self.floatvalue)
        self.OnChange(None)

    def OnValidationSuccess(self):
        self.valid = True
        self.SetBackgroundColour(wx.NullColour)
        self.Refresh()

    def OnValidationFailed(self):
        self.valid = False
        self.SetBackgroundColour(wx.Colour(255, 200, 200))
        self.Refresh()

    def GetFloat(self):
        return self.floatvalue

    def SetValue(self, value):
        self.floatvalue = float(value)
        wx.TextCtrl.SetValue(self, str(value))

    def ChangeValue(self, value):
        self.floatvalue = float(value)
        wx.TextCtrl.ChangeValue(self, str(value))

    def IsValid(self):
        return self.valid

    def SetRange(self, *args):
        if len(args) == 1:
            self.min = args[0][0]
            self.max = args[0][1]
        elif len(args) == 2:
            self.min = args[0]
            self.max = args[1]
        else:
            raise ValueError("SetRange requires 2 arguments or a 2-item tuple")

        assert self.min < self.max

    def SetMin(self, value):
        self.min = value
        self.Validate()

    def SetMax(self, value):
        self.max = value
        self.Validate()

    def SetDefault(self, value):
        self.default = value
        self.Validate()




class ListSelectCtrl(wx.Panel):
    
    def __init__(self):
        p = wx.PrePanel()
        self.PostCreate(p)

        # This is the 'official' way to hook the creation of the object
        #self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        # This is the way that actually works, courtesy of:
        # http://aspn.activestate.com/ASPN/Mail/Message/wxPython-users/2169189
        self.Bind(wx.EVT_SIZE, self.OnCreate)


    def OnCreate(self, evt):
        _verbose('Creating ListSelectCtrl')

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(mainsizer)

        # Available entries
        s1 = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(s1, 1, wx.EXPAND)
        s1.Add(wx.StaticText(self, label = 'Available fields'))
        self.list_avail = wx.ListBox(self, style = wx.LB_SINGLE)
        s1.Add(self.list_avail, 1, wx.EXPAND)

        # Add/remove/up/down
        s2 = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(s2, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 4)
        self.button_add = wx.Button(self, label = '&Add', 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_add, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_remove = wx.Button(self, label = '&Remove', 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_remove, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_up = wx.Button(self, label = 'Move &up', 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_up, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_down = wx.Button(self, label = 'Move &down', 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_down, 0, wx.EXPAND)

        # Selected entries
        s3 = wx.BoxSizer(wx.VERTICAL)
        mainsizer.Add(s3, 1, wx.EXPAND)
        s3.Add(wx.StaticText(self, label = 'Selected fields'))
        self.list_sel = wx.ListBox(self, style = wx.LB_SINGLE)
        s3.Add(self.list_sel, 1, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnAdd, self.button_add)
        self.Bind(wx.EVT_BUTTON, self.OnRemove, self.button_remove)
        self.Bind(wx.EVT_BUTTON, self.OnUp, self.button_up)
        self.Bind(wx.EVT_BUTTON, self.OnDown, self.button_down)

        # Make sure this is only called once
        self.Unbind(wx.EVT_SIZE)
        evt.Skip()

    
    def Reset(self):
        self.list_avail.Clear()
        self.list_sel.Clear()

        for i in self.available_items:
            self.list_avail.Append(i)


    def SetAvailable(self, items):
        self.available_items = items
        self.Reset()


    def SetSelection(self, items):
        self.Reset()
        
        for i in items:
            self.list_avail.SetStringSelection(i)
            self.OnAdd(None)


    def GetSelection(self):
        return self.list_sel.GetItems()


    def OnAdd(self, evt):
        sel = self.list_avail.GetSelection()

        if sel != -1:
            self.list_sel.Append(self.list_avail.GetString(sel))
            self.list_avail.Delete(sel)
            if sel == self.list_avail.GetCount():
                self.list_avail.SetSelection(sel - 1)
            else:
                self.list_avail.SetSelection(sel)


    def OnRemove(self, evt):
        sel = self.list_sel.GetSelection()

        if sel != -1:
            self.list_avail.Append(self.list_sel.GetString(sel))
            self.list_sel.Delete(sel)
            if sel == self.list_sel.GetCount():
                self.list_sel.SetSelection(sel - 1)
            else:
                self.list_sel.SetSelection(sel)


    def OnUp(self, evt):
        sel = self.list_sel.GetSelection()

        if sel > 0:
            item = self.list_sel.GetString(sel)
            self.list_sel.Delete(sel)
            self.list_sel.Insert(item, sel - 1)
            self.list_sel.SetSelection(sel - 1)


    def OnDown(self, evt):
        sel = self.list_sel.GetSelection()

        if sel != -1 and sel < (self.list_sel.GetCount() - 1):
            item = self.list_sel.GetString(sel)
            self.list_sel.Delete(sel)
            self.list_sel.Insert(item, sel + 1)
            self.list_sel.SetSelection(sel + 1)



class PresetChooser(wx.Panel):

    def __init__(self):
        p = wx.PrePanel()
        self.PostCreate(p)

        # This is the 'official' way to hook the creation of the object
        #self.Bind(wx.EVT_WINDOW_CREATE, self.OnCreate)
        # This is the way that actually works, courtesy of:
        # http://aspn.activestate.com/ASPN/Mail/Message/wxPython-users/2169189
        self.Bind(wx.EVT_SIZE, self.OnCreate)

    
    def OnCreate(self, evt):
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

        # Make sure this is only called once
        self.Unbind(wx.EVT_SIZE)
        evt.Skip()


    def SetPresets(self, presets):
        self.presets = presets
        self.choice.Clear()
        self.choice.SetItems(self.presets.keys())


    def Refresh(self):
        key = self.choice.GetStringSelection()
        self.choice.Clear()
        self.choice.SetItems(self.presets.keys())
        if key and key in self.presets:
            self.choice.SetStringSelection(key)
            self.do_load(self.presets[key])


    def OnChange(self, evt):
        self.do_load(self.presets[self.choice.GetStringSelection()])


    def OnSave(self, evt):
        item = self.do_get()
        key = wx.GetTextFromUser("Save preset as:", "DO3SE", self.choice.GetStringSelection(), self)

        if key and (not key in self.presets or \
                wx.MessageBox("Overwrite existing preset '%s'?" % (key), 'DO3SE', 
                    wx.YES_NO | wx.ICON_QUESTION | wx.NO_DEFAULT, self) == wx.YES):
            self.presets[key] = item
            self.Refresh()
            self.choice.SetStringSelection(key)
            self.do_load(self.presets[key])

    
    def OnDelete(self, evt):
        key = self.choice.GetStringSelection()

        if key and wx.MessageBox("Delete preset '%s'?" % (key), 'DO3SE', 
                wx.YES_NO | wx.ICON_WARNING, self) == wx.YES:
            del self.presets[key]
            self.Refresh()



class ChoiceDialog(wx.Dialog):
    
    def __init__(self, *args, **kwargs):
        wx.Dialog.__init__(self, *args, **kwargs)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.message = wx.StaticText(self, label = '')
        sizer.Add(self.message, 0, wx.TOP | wx.LEFT | wx.RIGHT | wx.EXPAND, 4)
        self.choice = wx.Choice(self)
        sizer.Add(self.choice, 0, wx.ALL | wx.EXPAND, 4)
        btns = wx.StdDialogButtonSizer()
        sizer.Add(btns, 0, wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND | wx.ALIGN_RIGHT, 4)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, '&Cancel')
        btns.AddButton(self.button_cancel)
        self.button_ok = wx.Button(self, wx.ID_OK, '&Ok')
        btns.AddButton(self.button_ok)
        btns.Realize()
        
        self.SetMinSize(sizer.GetMinSize())
        self.SetSize(sizer.GetMinSize())


    def SetMessage(self, message):
        self.message.SetLabel(message)


    def SetChoices(self, choices):
        self.choice.SetItems(choices)
        self.choice.SetSelection(0)


    def GetChoice(self):
        return self.choice.GetStringSelection()




def GetSingleChoice(parent, message, caption, choices):
    cd = ChoiceDialog(parent, title = caption)
    cd.SetMessage(message)
    cd.SetChoices(choices)
    
    if cd.ShowModal() == wx.ID_OK:
        choice = cd.GetChoice()
    else:
        choice = ''

    cd.Destroy()

    return choice
