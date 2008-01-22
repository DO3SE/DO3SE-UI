import wx
import os

from app import logging, app
import wxext
import maps
from dataset import Dataset


# Keep track of all the results windows
result_windows = []
result_windowcount = 0
result_recent_dir = ''


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
        wx.FileHistory.__init__(self, 9, wx.ID_FILE1)
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
        # Recently opened directory
        self.recent_dir = ''

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
        bClose = wx.Button(self.pMain, wx.ID_EXIT)
        s3.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_exit, bClose)
        bRun = wx.Button(self.pMain, label='&Run')
        s3.Add(bRun, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_run, bRun)


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
        self.inputs = wxext.ListSelectCtrl(p1)
        s3.Add(self.inputs, 1, wx.EXPAND|wx.ALL, 6)
        self.inputs.SetAvailable(maps.inputs.values())
        # Header trim
        s4 = wx.BoxSizer(wx.HORIZONTAL)
        s3.Add(s4, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        s4.Add(wx.StaticText(p1, \
            label='Number of lines to trim from beginning of file (e.g. for column headers)'),
            0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 6)
        self.inputs_trim = wx.SpinCtrl(p1, min=0, max=10, initial=0, style=wx.SP_ARROW_KEYS)
        s4.Add(self.inputs_trim, 0, wx.EXPAND)
        # List selector get-/setvalues callbacks
        def f():
            return {
                'fields': maps.inputs.rmap(self.inputs.GetSelection()),
                'trim': self.inputs_trim.GetValue(),
            }
        presets.getvalues = f
        def f(v):
            self.inputs.SetSelection(maps.inputs.map(v['fields']))
            self.inputs_trim.SetValue(v['trim'])
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
        self.outputs = wxext.ListSelectCtrl(p2)
        s4.Add(self.outputs, 1, wx.EXPAND|wx.ALL, 6)
        self.outputs.SetAvailable(maps.outputs.values())
        # List selector get-/setvalues callbacks
        def f(): return maps.outputs.rmap(self.outputs.GetSelection())
        presets1.getvalues = f
        def f(v): self.outputs.SetSelection(maps.outputs.map(v))
        presets1.setvalues = f


    def _init_menu(self):
        # Menu bar
        mb = wx.MenuBar()
        self.SetMenuBar(mb)

        # 'File' menu
        mFile = wx.Menu()
        # File -> Run
        id = wx.NewId()
        mFile.Append(id, 'Run\tCtrl+R')
        self.Bind(wx.EVT_MENU, self._on_run, id = id)
        # File -> Run recent
        mFileRecent = wx.Menu()
        mFile.AppendSubMenu(mFileRecent, 'Run &Recent')
        self.filehistory.UseMenu(mFileRecent)
        self.filehistory.AddFilesToMenu()
        self.Bind(wx.EVT_MENU, self._on_run_recent, 
                id = wx.ID_FILE1, id2 = wx.ID_FILE9)
        # File -> Quit
        mFile.AppendSeparator()
        mFile.Append(wx.ID_EXIT)
        mb.Append(mFile, '&File')
        self.Bind(wx.EVT_MENU, self._on_exit, id = wx.ID_EXIT)


    def _on_run(self, evt):
        fd = wx.FileDialog(self, message = 'Open data file',
                defaultDir = self.recent_dir,
                wildcard = 'Comma-separated values (*.csv)|*.csv|All files (*.*)|*',
                style = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            self.recent_dir = fd.GetDirectory()
            path = fd.GetPath()
            self._run_file(path)


    def _on_run_recent(self, evt):
        self._run_file(self.filehistory.GetHistoryFile(evt.GetId() - wx.ID_FILE1))


    def _on_exit(self, evt):
        # TODO: Close all results windows first
        global results_windows
        for w in result_windows: w.Close()
        self.Close()


    def _run_file(self, path):
        if not os.access(path, os.R_OK):
            wx.MessageBox("Could not read the specified file", 
                    wx.OK|wx.ICON_ERROR, self)
            return

        d = Dataset(path, maps.inputs.rmap(self.inputs.GetSelection()),
                self.inputs_trim.GetValue())
        self.filehistory.AddFileToHistory(path)
        d.run()
        r = ResultsWindow(d, {
            'inputs': list(maps.inputs.rmap(self.inputs.GetSelection())),
            'inputs_trim': int(self.inputs_trim.GetValue()),
            'outputs': list(maps.outputs.rmap(self.outputs.GetSelection())),
        })
        r.Show()


class ResultsWindow(wx.Frame):
    def __init__(self, dataset, settings):
        wx.Frame.__init__(self, app.toplevel)
        self.dataset = dataset
        self.settings = settings

        self._init_frame()

        self.Bind(wx.EVT_CLOSE, self._on_close)

    
    def _init_frame(self):
        global result_windows, result_windowcount
        result_windows.append(self)
        result_windowcount += 1

        self.SetSize((800, 600))
        self.SetTitle("DOSE - Results (%d)" % result_windowcount)

        s0 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s0)

        placeholder = wx.Panel(self)
        s0.Add(placeholder, 1, wx.EXPAND)

        s1 = wx.BoxSizer(wx.HORIZONTAL)
        s0.Add(s1, 0, wx.ALIGN_RIGHT|wx.ALL, 6)
        bClose = wx.Button(self, wx.ID_CLOSE)
        s1.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, lambda evt: self.Close(), bClose)
        bSave = wx.Button(self, wx.ID_SAVE)
        s1.Add(bSave, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_save, bSave)


    def _on_close(self, evt):
        global result_windows
        logging.debug("Cleaning up results window")
        result_windows.remove(self)
        evt.Skip()


    def _on_save(self, evt):
        global result_recent_dir
        fd = wx.FileDialog(self, message = 'Save results',
                defaultDir = result_recent_dir,
                wildcard = 'Comma-separated values (*.csv)|*.csv|All files (*.*)|*',
                style = wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            result_recent_dir = fd.GetDirectory()
            path = fd.GetPath()
            if not path.split('.')[-1] == 'csv': path = path + '.csv'
            self.dataset.save(path, self.settings['outputs'], headers=True)
            wx.MessageDialog(self, message = 'Results saved!',
                    style = wx.OK|wx.ICON_INFORMATION)
        
