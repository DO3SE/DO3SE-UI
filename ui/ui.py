import wx
import os

from FloatSpin import FloatSpin
from app import logging, app
import wxext
import maps
from dataset import Dataset
import panels


# Keep track of all the results windows
result_windows = list()
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

        self.site = dict()
        self.veg = dict()

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
        pInput = panels.InputParams(nbMain)
        nbMain.AddPage(pInput, "Input format")

        ### 'Site parameters' tab ###
        pSite = panels.SiteParams(nbMain)
        nbMain.AddPage(pSite, "Site parameters")

        ### 'Vegetation parameters' tab ###
        pVeg = panels.VegParams(nbMain)
        nbMain.AddPage(pVeg, "Vegetation parameters")
            
        ### 'Output' tab ###
        pOutput = panels.OutputParams(nbMain)
        nbMain.AddPage(pOutput, 'Output')


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
        d.run(self.get_site_params(), None)
        r = ResultsWindow(d, {
            'inputs': list(maps.inputs.rmap(self.lsInputs.GetSelection())),
            'inputs_trim': int(self.spinInputTrim.GetValue()),
            'outputs': list(maps.outputs.rmap(self.slOutputs.GetSelection())),
            'outputs_headers': self.chkOutputHeaders.GetValue(),
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
            self.dataset.save(path, self.settings['outputs'], headers=self.settings['outputs_headers'])
            wx.MessageDialog(self, message = 'Results saved!',
                    style = wx.OK|wx.ICON_INFORMATION)
        
