import wx
import os

from FloatSpin import FloatSpin
from app import logging, app
import wxext
import maps
from dataset import Dataset, InsufficientTrimError, InvalidFieldCountError
import panels
import dose


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
        self.SetSize((600,600))
        self.SetTitle(app.title)

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
        bClose = wx.Button(p, wx.ID_EXIT)
        sButtons.Add(bClose, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_exit, bClose)
        bRun = wx.Button(p, label='&Run')
        sButtons.Add(bRun, 0, wx.EXPAND|wx.LEFT, 6)
        self.Bind(wx.EVT_BUTTON, self._on_run, bRun)


        ### 'Input' tab ###
        self.Input = panels.InputParams(nbMain)
        nbMain.AddPage(self.Input, "Input format")

        ### 'Site parameters' tab ###
        self.Site = panels.SiteParams(nbMain)
        nbMain.AddPage(self.Site, "Site parameters")

        ### 'Vegetation parameters' tab ###
        self.Veg = panels.VegParams(nbMain)
        nbMain.AddPage(self.Veg, "Vegetation parameters")


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
        class RequiredFieldError:
            def __init__(self, fields):
                if len(fields) == 1:
                    wx.MessageBox("Required field missing: %s" % maps.inputs.map(fields)[0],
                            app.title, wx.OK|wx.ICON_ERROR, app.toplevel)

                else:
                    wx.MessageBox("At least one of the following fields are required:\n\n" + 
                            "\n".join(maps.inputs.map(fields)), app.title, 
                            wx.OK|wx.ICON_ERROR, app.toplevel)

        self.filehistory.AddFileToHistory(path)

        fields = self.Input.GetFields()

        # Requiried fields
        required = ['dd', 'hr', 'ts_c', 'vpd', 'uh_zr', 'precip', 'p', 'o3_ppb_zr']
        try:
            for f in required:
                if not f in fields:
                    raise RequiredFieldError([f])
        except RequiredFieldError:
            return

        # PAR/Global radiation
        try:
            if 'par' in fields and 'r' in fields:
                def f(): pass
                par_r = f
            elif 'par' in fields:
                par_r = lambda : dose.inputs.derive_r()
            elif 'r' in fields:
                par_r = lambda : dose.inputs.derive_par()
            else:
                raise RequiredFieldError(['par', 'r'])
        except RequiredFieldError:
            return

        # Calculate net radiation if not supplied
        if 'rn' in fields:
            rn = dose.irradiance.copy_rn
        else:
            rn = dose.irradiance.calc_rn

        if not os.access(path, os.R_OK):
            wx.MessageBox("Could not read the specified file", 
                    wx.OK|wx.ICON_ERROR, self)
            return

        # Load the data, set the parameters
        try:
            d = Dataset(path, self.Input.GetFields(), self.Input.GetTrim(), 
                    self.Site.getvalues(), self.Veg.getvalues())
        # We already warn the user about these, so don't raise them - just fail
        # to run the dataset
        except InsufficientTrimError: return
        # Set up the calculation changes
        d.par_r = par_r
        d.rn = rn

        try:
            r = ResultsWindow(d, self.recent_dir)
        except InvalidFieldCountError: return
        r.Show()


class ResultsWindow(wx.Frame):
    def __init__(self, dataset, startdir):
        self.dataset = dataset
        self.startdir = startdir

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
                    app.title, wx.OK|wx.ICON_WARNING, app.toplevel)

        wx.Frame.__init__(self, app.toplevel)
        self._init_frame()

        self.Bind(wx.EVT_CLOSE, self._on_close)

    
    def _init_frame(self):
        # Give the window a number, and store a reference to it
        global result_windows, result_windowcount
        result_windows.append(self)
        result_windowcount += 1

        # Set size and title
        self.SetSize((800, 600))
        self.SetTitle("%s - Results (%d)" % (app.title, result_windowcount))

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

        pSave = panels.Save(nbMain, self.dataset, self.startdir)
        nbMain.AddPage(pSave, "Save to file")


    def _on_close(self, evt):
        global result_windows
        logging.debug("Cleaning up results window")
        result_windows.remove(self)
        evt.Skip()
