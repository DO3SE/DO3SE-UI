import wx
from wx import xrc

import application

windowcount = 0
prevdir = ""

class ResultsWindow(wx.Frame):
    
    def __init__(self, dataset):
        wx.Frame.__init__(self, None)

        self.dataset = dataset

        self.InitFrame()

    
    def InitFrame(self):
        global windowcount

        s0 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s0)
        self.panel = application.xrcres.LoadPanel(self, 'window_results')
        s0.Add(self.panel, 1, wx.EXPAND)

        windowcount += 1
        self.SetSize((750, 550))
        self.SetTitle("DOSE - Results (%s)" % windowcount)

        buttonpanel = xrc.XRCCTRL(self, "panel_results_buttons")
        buttonpanel.SetBackgroundColour((255,255,255))
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        buttonpanel.SetSizer(s1)
        saveas = wx.Button(buttonpanel, wx.ID_SAVEAS)
        s1.Add(saveas, 0, wx.EXPAND)
        close = wx.Button(buttonpanel, wx.ID_CLOSE)
        s1.Add(close, 0, wx.EXPAND)

        self.Bind(wx.EVT_BUTTON, self.OnSave, saveas)


    def OnSave(self, evt):
        global prevdir

        fd = wx.FileDialog(self, message = "Save data", 
                defaultDir = prevdir,
                wildcard = 'Comma-Separated Values (*.csv)|*.csv|All files (*.*)|*.*',
                style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            prevdir = fd.GetDirectory()
            path = fd.GetPath()

            self.dataset.Save(path)
