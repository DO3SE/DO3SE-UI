import wx
from wx.lib import plot

class StaticBoxCanvas(wx.StaticBoxSizer):
    def __init__(self, parent, label):
        wx.StaticBoxSizer.__init__(self, wx.StaticBox(parent, label=label), wx.VERTICAL)
        self.canvas = plot.PlotCanvas(parent)
        self.canvas.SetEnableTitle(False)
        self.canvas.SetFontSizeLegend(10)
        self.Add(self.canvas, 1, wx.EXPAND)
