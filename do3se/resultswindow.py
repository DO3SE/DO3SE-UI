import wx

from datapanel import DataPanel
from savepanel import SavePanel

class ResultsWindow(wx.Frame):
    def __init__(self, parent, dataset, startdir, id):
        self.parent = parent
        self.dataset = dataset
        self.startdir = startdir
        self.id = id

        # Run the dataset before anything else - if there was an error, don't 
        # bother creating the window at all (caught by the creator)
        resultcount, skippedrows = self.dataset.run()

        # Notify the user of any problems encountered while running the dataset
        if skippedrows > 0:
            wx.MessageBox(("%s incomplete data rows were skipped, but %s rows "+ \
                    "were processed normally.  If this matches the number of "+ \
                    "data rows in your file (not including headers) then "+ \
                    "there is nothing to worry about, otherwise check your "+ \
                    "data file for missing values.") % (skippedrows, resultcount), 
                    parent.app.title, wx.OK|wx.ICON_WARNING, parent)

        wx.Frame.__init__(self, parent)
        self._init_frame()

    
    def _init_frame(self):
        # Set size and title
        self.SetSize((800, 600))
        self.SetTitle("%s - Results (%d)" % (self.parent.app.title, self.id))

        ### Main panel ###
        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)
        p = wx.Panel(self)
        s.Add(p, 1, wx.EXPAND)
        sMain = wx.BoxSizer(wx.VERTICAL)
        p.SetSizer(sMain)
        
        # Create notebook
        nbMain = wx.Notebook(p)
        sMain.Add(nbMain, 1, wx.EXPAND|wx.ALL, 6)
        # Create bottom buttons
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        sMain.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bClose = wx.Button(p, wx.ID_CLOSE)
        sButtons.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.Close(), bClose)

        ### Data panel ###
        pData = DataPanel(nbMain, self.dataset)
        nbMain.AddPage(pData, "Data")

        ### Save to File panel ###
        pSave = SavePanel(self.parent.app, nbMain, self.dataset, self.startdir)
        nbMain.AddPage(pSave, "Save to file")
