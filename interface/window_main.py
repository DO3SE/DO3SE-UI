import wx


class PButton(wx.Panel):
    def __init__(self, parent, label):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label = label), border = 20, \
                flag = wx.ALIGN_CENTRE | wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT)
        self.SetSizer(sizer)

class ButtonPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(PButton(self, "This is a button"), flag = wx.EXPAND, proportion = 1)
        sizer.Add(PButton(self, "This is another button"), flag = wx.EXPAND, proportion = 1)
        sizer.Add(PButton(self, "This is yet another button"), flag = wx.EXPAND, proportion = 1)
        self.SetBackgroundColour(wx.GREEN)
        self.SetSizer(sizer)

class MDIPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, label="FOOOOO"), flag = wx.EXPAND)
        self.SetBackgroundColour(wx.RED)
        self.SetSizer(sizer)

class Main(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        fgs1 = wx.FlexGridSizer(cols = 2, hgap = 5, vgap = 5)
        fgs1.SetSizeHints(self)
        self.SetSizer(fgs1)
        fgs1.SetFlexibleDirection(wx.HORIZONTAL)
        fgs1.AddGrowableCol(1, 1)

        fgs1.Add(ButtonPanel(self), flag = wx.EXPAND)
        fgs1.Add(MDIPanel(self), flag = wx.EXPAND)
        
