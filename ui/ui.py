import wx

from app import logging
from config import config, add_recent_file
import wxext

class FileHistory(wx.FileHistory):
    """Recent file history

    A wrapper around wxFileHistory which uses the application config to load the
    initial set of recent files, and keeps the config up to date every time a 
    recent file is added.
    """
    def __init__(self):
        """Constructor

        Create the wxFileHistory in the way we want and load from the config.
        """
        wx.FileHistory.__init__(self, 9, wx.ID_FILE)
        for p in config['filehistory']: wx.FileHistory.AddFileToHistory(self, p)

    def AddFileToHistory(self, path):
        """Add file to history

        Add a file to the recent files list in the normal way, but also add it 
        to the config.
        """
        wx.FileHistory.AddFileToHistory(self, path)
        add_recent_file(path)



class MainWindow(wx.Frame):
    """Main application window

    This is where the input file is selected, parameterisation is done, formats
    are defined, etc.
    """

    def __init__(self):
        """Constructor

        Initialise the window.
        """
        wx.Frame.__init__(self, None)

        # File history
        self.filehistory = FileHistory()

        # Initialise
        self._init_frame()
        self._init_menu()

    def _init_frame(self):
        """Initialise the user interface

        Add all controls to the window, set everything up except for the menu.
        """

        # Set window size and title
        self.SetSize((800,600))
        self.SetTitle('DOSE Model')

        # Main window sizer
        s0 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s0)


        ### Placeholder panel ###
        self.pPlaceholder = wx.Panel(self)
        s0.Add(self.pPlaceholder, 1, wx.EXPAND)
        s1 = wx.BoxSizer(wx.HORIZONTAL)
        self.pPlaceholder.SetSizer(s1)
        # Instructions!
        s1.Add(wx.StaticText(self.pPlaceholder, 
            label="To start, open a file using the 'File -> Open...' menu.",
            style=wx.ALIGN_CENTER), 1, wx.ALIGN_CENTER_VERTICAL)


        ### Main panel ###
        self.pMain = wx.Panel(self)
        s0.Add(self.pMain, 1, wx.ALL|wx.EXPAND, 6)
        s2 = wx.BoxSizer(wx.VERTICAL)
        self.pMain.SetSizer(s2)
        # Create notebook
        nbMain = wx.Notebook(self.pMain)
        nbMain.SetBackgroundColour((0,0,0))
        s2.Add(nbMain, 1, wx.EXPAND)


        ### 'Input' tab ###
        p1 = wx.Panel(nbMain)
        nbMain.AddPage(p1, 'Input')
        s3 = wx.BoxSizer(wx.VERTICAL)
        p1.SetSizer(s3)
        presets = wxext.PresetChooser(p1)
        s3.Add(presets, 0, wx.EXPAND|wx.ALL, 6)


    def _init_menu(self):
        # Menu bar
        mb = wx.MenuBar()
        self.SetMenuBar(mb)

        # 'File' menu
        mFile = wx.Menu()
        mFile.Append(wx.ID_OPEN)
        mFileRecent = wx.Menu()
        mFile.AppendSubMenu(mFileRecent, 'Open &Recent')
        self.filehistory.UseMenu(mFileRecent)
        self.filehistory.AddFilesToMenu()
        mFile.Append(wx.ID_CLOSE)
        mFile.AppendSeparator()
        mFile.Append(wx.ID_EXIT)
        mb.Append(mFile, '&File')
