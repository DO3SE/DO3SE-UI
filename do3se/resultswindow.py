import wx

from datapanel import DataPanel
from savepanel import SavePanel

class ResultsWindow(wx.Frame):
    def __init__(self, app, parent, results, title):
        wx.Frame.__init__(self, parent)
        self.SetSize((800, 600))
        self.SetTitle('%s - %s' % (app.GetAppName(), title))
        self.SetExtraStyle(wx.WS_EX_BLOCK_EVENTS)

        self.app = app
        self.results = results


        ### Main panel ###
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)
        p = wx.Panel(self)
        s.Add(p, 1, wx.EXPAND)
        sMain = wx.BoxSizer(wx.VERTICAL)
        p.SetSizer(sMain)
        
        # Create notebook
        nbMain = wx.Notebook(p)
        sMain.Add(nbMain, 1, wx.EXPAND|wx.ALL, 5)
        # Create bottom buttons
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        sMain.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        bClose = wx.Button(p, wx.ID_CLOSE)
        sButtons.Add(bClose, 0, wx.EXPAND|wx.LEFT, 5)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.Close(), bClose)

        ### Data panel ###
        pData = DataPanel(nbMain, self.results.data)
        nbMain.AddPage(pData, "Data")

        ### Save to File panel ###
        pSave = SavePanel(self.app, nbMain, self.results)
        nbMain.AddPage(pSave, "Save to file")
