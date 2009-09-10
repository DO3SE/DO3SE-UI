import wx

class ListSelectCtrl(wx.Panel):
    
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

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
        self.button_add = wx.Button(self, wx.ID_ADD, 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_add, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_remove = wx.Button(self, wx.ID_REMOVE, 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_remove, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_up = wx.Button(self, wx.ID_UP, 
                style = wx.BU_EXACTFIT)
        s2.Add(self.button_up, 0, wx.EXPAND)
        s2.AddSpacer(4)
        self.button_down = wx.Button(self, wx.ID_DOWN, 
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

    
    def Reset(self):
        """
        Reset the ListSelectCtrl to its initial state (with no items selected)
        """
        self.list_avail.Clear()
        self.list_sel.Clear()

        for i in self.available_items:
            self.list_avail.Append(i[0], i[1])


    def SetAvailable(self, items):
        """
        Set the available choices
        
        Replace the list of choices that are available.  "items" is a list of
        (text, clientdata) pairs.
        """
        self.available_items = items
        self.Reset()


    def SetSelection(self, items):
        """
        Set the current selection

        Set the currently selected items by simulating the way the user would
        select them and click the add button.
        """
        self.Reset()
        
        for i in items:
            self.list_avail.SetStringSelection(i)
            self.OnAdd(None)


    def GetSelection(self):
        return self.list_sel.GetItems()


    def GetSelectionWithData(self):
        """
        Get the current selection as (text, clientdata) pairs
        """
        return ((self.list_sel.GetString(n), self.list_sel.GetClientData(n))
                for n in xrange(self.list_sel.GetCount()))


    def OnAdd(self, evt):
        sel = self.list_avail.GetSelection()

        if sel != -1:
            self.list_sel.Append(self.list_avail.GetString(sel),
                                 self.list_avail.GetClientData(sel))
            self.list_avail.Delete(sel)
            if sel == self.list_avail.GetCount():
                self.list_avail.SetSelection(sel - 1)
            else:
                self.list_avail.SetSelection(sel)


    def OnRemove(self, evt):
        sel = self.list_sel.GetSelection()

        if sel != -1:
            self.list_avail.Append(self.list_sel.GetString(sel),
                                   self.list_sel.GetClientData(sel))
            self.list_sel.Delete(sel)
            if sel == self.list_sel.GetCount():
                self.list_sel.SetSelection(sel - 1)
            else:
                self.list_sel.SetSelection(sel)


    def OnUp(self, evt):
        sel = self.list_sel.GetSelection()

        if sel > 0:
            item = self.list_sel.GetString(sel)
            cdata = self.list_sel.GetClientData(sel)
            self.list_sel.Delete(sel)
            self.list_sel.Insert(item, sel - 1, cdata)
            self.list_sel.SetSelection(sel - 1)


    def OnDown(self, evt):
        sel = self.list_sel.GetSelection()

        if sel != -1 and sel < (self.list_sel.GetCount() - 1):
            item = self.list_sel.GetString(sel)
            cdata = self.list_sel.GetClientData(sel)
            self.list_sel.Delete(sel)
            self.list_sel.Insert(item, sel + 1, cdata)
            self.list_sel.SetSelection(sel + 1)
