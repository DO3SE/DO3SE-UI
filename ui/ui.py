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

        ### Main panel ###
        sMain = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sMain)
        # Create notebook
        nbMain = wx.Notebook(self)
        sMain.Add(nbMain, 1, wx.EXPAND|wx.ALL, 6)
        # Create bottom buttons
        sButtons = wx.BoxSizer(wx.HORIZONTAL)
        sMain.Add(sButtons, 0, wx.ALL|wx.ALIGN_RIGHT, 6)
        bClose = wx.Button(self, wx.ID_EXIT)
        sButtons.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_exit, bClose)
        bRun = wx.Button(self, label='&Run')
        sButtons.Add(bRun, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_run, bRun)


        ### 'Input' tab ###
        pInput = wx.Panel(nbMain)
        nbMain.AddPage(pInput, 'Input')
        sInput = wx.BoxSizer(wx.VERTICAL)
        pInput.SetSizer(sInput)
        # Preset manager
        presetInput = wxext.PresetChooser(pInput)
        sInput.Add(presetInput, 0, wx.EXPAND|wx.ALL, 6)
        presetInput.SetPresets(app.config['preset.inputs'])
        # Preset manager post_update() callback
        def f():
            app.config['preset.inputs'] = presetInput.GetPresets()
            app.config.sync()
        presetInput.post_update = f
        # List selector
        self.lsInputs = wxext.ListSelectCtrl(pInput)
        sInput.Add(self.lsInputs, 1, wx.EXPAND|wx.ALL, 6)
        self.lsInputs.SetAvailable(maps.inputs.values())
        # Header trim
        sTrim = wx.BoxSizer(wx.HORIZONTAL)
        sInput.Add(sTrim, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        sTrim.Add(wx.StaticText(pInput, \
            label='Number of lines to trim from beginning of file (e.g. for column headers)'),
            0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 6)
        self.spinInputTrim = wx.SpinCtrl(pInput, min=0, max=10, initial=0, style=wx.SP_ARROW_KEYS)
        sTrim.Add(self.spinInputTrim, 0, wx.EXPAND)
        # Preset manager get-/setvalues callbacks
        def f():
            return {
                'fields': maps.inputs.rmap(self.lsInputs.GetSelection()),
                'trim': self.spinInputTrim.GetValue(),
            }
        presetInput.getvalues = f
        def f(v):
            self.lsInputs.SetSelection(maps.inputs.map(v['fields']))
            self.spinInputTrim.SetValue(v['trim'])
        presetInput.setvalues = f


        ### 'Output' tab ###
        pOutput = wx.Panel(nbMain)
        nbMain.AddPage(pOutput, 'Output')
        sOutput = wx.BoxSizer(wx.VERTICAL)
        pOutput.SetSizer(sOutput)
        # Preset manager
        presetOutput = wxext.PresetChooser(pOutput)
        sOutput.Add(presetOutput, 0, wx.EXPAND|wx.ALL, 6)
        presetOutput.SetPresets(app.config['preset.outputs'])
        # Preset manager post_update() callback
        def f():
            app.config['preset.outputs'] = presetOutput.GetPresets()
            app.config.sync()
        presetOutput.post_update = f
        # List selector
        self.slOutputs = wxext.ListSelectCtrl(pOutput)
        sOutput.Add(self.slOutputs, 1, wx.EXPAND|wx.ALL, 6)
        self.slOutputs.SetAvailable(maps.outputs.values())
        # "Include column headers?"
        
        # Preset manager get-/setvalues callbacks
        def f(): return maps.outputs.rmap(self.slOutputs.GetSelection())
        presetOutput.getvalues = f
        def f(v): self.slOutputs.SetSelection(maps.outputs.map(v))
        presetOutput.setvalues = f


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

        d = Dataset(path, maps.inputs.rmap(self.lsInputs.GetSelection()),
                self.spinInputTrim.GetValue())
        self.filehistory.AddFileToHistory(path)
        d.run()
        r = ResultsWindow(d, {
            'inputs': list(maps.inputs.rmap(self.lsInputs.GetSelection())),
            'inputs_trim': int(self.spinInputTrim.GetValue()),
            'outputs': list(maps.outputs.rmap(self.slOutputs.GetSelection())),
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
        
