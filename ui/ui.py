import wx

from app import logging, app
import wxext
import maps

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
        for p in app.config['filehistory']: wx.FileHistory.AddFileToHistory(self, p)

    def AddFileToHistory(self, path):
        """Add file to history

        Add a file to the recent files list in the normal way, but also add it 
        to the config.
        """
        wx.FileHistory.AddFileToHistory(self, path)
        app.AddFileToHistory(path)



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
        self.pPlaceholder.Hide()

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
        s0.Add(self.pMain, 1, wx.EXPAND)
        s2 = wx.BoxSizer(wx.VERTICAL)
        self.pMain.SetSizer(s2)
        # Create notebook
        nbMain = wx.Notebook(self.pMain)
        s2.Add(nbMain, 1, wx.EXPAND|wx.ALL, 6)
        # Create bottom buttons
        s3 = wx.BoxSizer(wx.HORIZONTAL)
        s2.Add(s3, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bClose = wx.Button(self.pMain, wx.ID_CLOSE)
        s3.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.Close(), bClose)
        bRun = wx.Button(self.pMain, label='&Run')
        s3.Add(bRun, 0, wx.EXPAND|wx.LEFT, 6)


        ### 'Input' tab ###
        p1 = wx.Panel(nbMain)
        nbMain.AddPage(p1, 'Input')
        s3 = wx.BoxSizer(wx.VERTICAL)
        p1.SetSizer(s3)
        # Preset manager
        presets = wxext.PresetChooser(p1)
        s3.Add(presets, 0, wx.EXPAND|wx.ALL, 6)
        presets.SetPresets(app.config['preset.inputs'])
        # Preset manager post_update() callback
        def f():
            app.config['preset.inputs'] = presets.GetPresets()
            app.config.sync()
        presets.post_update = f
        # List selector
        fields = wxext.ListSelectCtrl(p1)
        s3.Add(fields, 1, wx.EXPAND|wx.ALL, 6)
        fields.SetAvailable(maps.inputs.values())
        # List selector get-/setvalues callbacks
        def f(): return maps.inputs.rmap(fields.GetSelection())
        presets.getvalues = f
        def f(v): fields.SetSelection(maps.inputs.map(v))
        presets.setvalues = f


        ### 'Output' tab ###
        p2 = wx.Panel(nbMain)
        nbMain.AddPage(p2, 'Output')
        s4 = wx.BoxSizer(wx.VERTICAL)
        p2.SetSizer(s4)
        # Preset manager
        presets1 = wxext.PresetChooser(p2)
        s4.Add(presets1, 0, wx.EXPAND|wx.ALL, 6)
        presets1.SetPresets(app.config['preset.outputs'])
        # Preset manager post_update() callback
        def f():
            app.config['preset.outputs'] = presets1.GetPresets()
            app.config.sync()
        presets1.post_update = f
        # List selector
        fields1 = wxext.ListSelectCtrl(p2)
        s4.Add(fields1, 1, wx.EXPAND|wx.ALL, 6)
        fields1.SetAvailable(maps.outputs.values())
        # List selector get-/setvalues callbacks
        def f(): return maps.outputs.rmap(fields1.GetSelection())
        presets1.getvalues = f
        def f(v): fields1.SetSelection(maps.outputs.map(v))
        presets1.setvalues = f


    def _init_menu(self):
        # Menu bar
        mb = wx.MenuBar()
        self.SetMenuBar(mb)

        # 'File' menu
        mFile = wx.Menu()
        # File -> Open
        mFile.Append(wx.ID_OPEN)
        # File -> Open recent
        mFileRecent = wx.Menu()
        mFile.AppendSubMenu(mFileRecent, 'Open &Recent')
        self.filehistory.UseMenu(mFileRecent)
        self.filehistory.AddFilesToMenu()
        # File -> Close
        mFile.Append(wx.ID_CLOSE)
        mFile.AppendSeparator()
        # File -> Quit
        mFile.Append(wx.ID_EXIT)
        mb.Append(mFile, '&File')
        self.Bind(wx.EVT_MENU, lambda evt: self.Close(), id = wx.ID_EXIT)
