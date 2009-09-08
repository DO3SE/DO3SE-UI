import wx

class StaticBox2Col(wx.StaticBoxSizer):
    def __init__(self, parent, label):
        wx.StaticBoxSizer.__init__(self, 
                wx.StaticBox(parent, label=label), wx.VERTICAL)
        self.fgs = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        #self.fgs.AddGrowableCol(0)
        #self.fgs.AddGrowableCol(1)
        self.Add(self.fgs, 1, wx.EXPAND|wx.ALL, 6)
