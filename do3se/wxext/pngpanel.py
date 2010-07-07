import wx

class PNGPanel(wx.Panel):
    def __init__(self, parent, filename):
        wx.Panel.__init__(self, parent)

        bmp = wx.Image(filename).ConvertToBitmap()
        self.SetSize((bmp.GetWidth(), bmp.GetHeight()))
        sb = wx.StaticBitmap(self, -1, bmp, (0, 0), (bmp.GetWidth(), bmp.GetHeight()))

        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)
        s.Add(sb, 1, wx.EXPAND)
