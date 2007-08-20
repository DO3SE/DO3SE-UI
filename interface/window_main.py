import wx

class NotebookPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        self.notebook = wx.Notebook(self)

        self.sizer.Add(self.notebook, flag = wx.EXPAND | wx.ALL, proportion = 1, border = 4)

class InputPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        outersizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(outersizer)

        self.sizer = wx.FlexGridSizer(cols = 2, vgap = 5, hgap = 5)
        self.sizer.SetFlexibleDirection(wx.HORIZONTAL)
        self.sizer.AddGrowableCol(1, 1)
        outersizer.Add(self.sizer, proportion = 1, flag = wx.EXPAND | wx.ALL, border = 4)
        
        self.sizer.Add(wx.StaticText(self, label = _("Input file") + ':'), flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        fpc = wx.FilePickerCtrl(self)
        self.sizer.Add(fpc, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)


class Main(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        nbp = NotebookPanel(self)
        self.sizer.Add(nbp, flag = wx.EXPAND, proportion = 1)

        ip  = InputPanel(nbp.notebook)

        nbp.notebook.AddPage(ip, "Input")
        
