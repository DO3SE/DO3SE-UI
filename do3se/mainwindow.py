import wx
import logging
import os

import model
from filehistory import FileHistory
from intropanel import IntroPanel
from inputpanel import InputPanel
from sitepanel import SitePanel
from vegetationpanel import VegetationPanel
from dataset import Dataset, InsufficientTrimError, InvalidFieldCountError
from resultswindow import ResultsWindow

class MainWindow(wx.Frame):
    """Main application window

    This is where the input file is selected, parameterisation is done, formats
    are defined, etc.
    """

    def __init__(self, app):
        """Constructor

        Initialise the window.
        """
        wx.Frame.__init__(self, None)

        # Application instance
        self.app = app

        # File history
        self.filehistory = FileHistory(self)
        # Recently opened directory
        self.recent_dir = ''

        # Results windows
        self.results_windows = list()

        # Initialise
        self._init_frame()
        self._init_menu()

    def _init_frame(self):
        """Initialise the user interface

        Add all controls to the window, set everything up except for the menu.
        """

        # Set window size and title
        self.SetSize((900,600))
        self.SetTitle(self.app.title)

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

        ### 'Introduction' tab ###
        self.Intro = IntroPanel(self.app, nbMain)
        nbMain.AddPage(self.Intro, "DO3SE model")

        ### 'Input' tab ###
        self.Input = InputPanel(self.app, nbMain)
        nbMain.AddPage(self.Input, "Input format")

        ### 'Site parameters' tab ###
        self.Site = SitePanel(self.app, nbMain)
        nbMain.AddPage(self.Site, "Site parameters")

        ### 'Vegetation parameters' tab ###
        self.Veg = VegetationPanel(self.app, nbMain)
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

        # 'Tools' menu
        mTools = wx.Menu()
        id = wx.NewId()
        mTools.Append(id, 'Dump settings')
        self.Bind(wx.EVT_MENU, self._on_dump_settings, id = id)
        id = wx.NewId()
        mTools.Append(id, 'Load settings')
        self.Bind(wx.EVT_MENU, self._on_load_settings, id = id)
        mb.Append(mTools, '&Tools')


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
        for w in self.results_windows:
            w.Close()
        if len(self.results_windows):
            logging.warning('Results windows still open: '
                    + str(len(self.results_windows)))
        self.Close()


    def _on_dump_settings(self, evt):
        from do3se.util.jsondict import JsonDict

        fd = wx.FileDialog(self, message = 'Dump settings',
                defaultDir=self.recent_dir,
                wildcard='JSON (*.json)|*.json|All files (*.*)|*',
                style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            path = fd.GetPath()
            if not path.split('.')[-1].lower() == 'json': path = path + '.json'
            jd = JsonDict(path)
            jd['input_format'] = self.Input.getvalues()
            jd['site_params'] = self.Site.getvalues()
            jd['veg_params'] = self.Veg.getvalues()
            jd.close()


    def _on_load_settings(self, evt):
        fd = wx.FileDialog(self, message='Load settings',
                defaultDir=self.recent_dir,
                wildcard='JSON (*.json)|*.json|All files (*.*)|*',
                style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
        response = fd.ShowModal()

        if response == wx.ID_OK:
            from do3se.util.jsondict import JsonDict
            jd = JsonDict(fd.GetPath())
            self.Input.setvalues(jd['input_format'])
            self.Site.setvalues(jd['site_params'])
            self.Veg.setvalues(jd['veg_params'])


    def _run_file(self, path):
        class RequiredFieldError:
            def __init__(self, app, fields):
                if len(fields) == 1:
                    wx.MessageBox("Required field missing: " + model.input_field_map[fields[0]]['long'],
                            app.title, wx.OK|wx.ICON_ERROR, app.toplevel)

                else:
                    wx.MessageBox("At least one of the following fields are required:\n\n" + 
                            "\n".join((model.input_field_map[x]['long'] for x in fields)), app.title, 
                            wx.OK|wx.ICON_ERROR, app.toplevel)

        self.filehistory.AddFileToHistory(path)

        fields = self.Input.GetFields()

        # Handle inputs marked as required
        required = (x['variable'] for x in model.input_fields if x['required'])
        try:
            for f in required:
                if not f in fields:
                    raise RequiredFieldError(self.app, [f])
        except RequiredFieldError:
            return

        # Handle more complicated situations: PAR/Global radiation
        try:
            if 'par' in fields and 'r' in fields:
                def f(): pass
                par_r = f
                logging.info("Both R and PAR present")
            elif 'par' in fields:
                par_r = lambda : model.inputs.derive_r()
                logging.info("Deriving R from PAR")
            elif 'r' in fields:
                par_r = lambda : model.inputs.derive_par()
                logging.info("Deriving PAR from R")
            else:
                raise RequiredFieldError(self.app, ['par', 'r'])
        except RequiredFieldError:
            return

        # Calculate net radiation if not supplied
        if 'rn' in fields:
            rn = model.irradiance.copy_rn
        else:
            rn = model.irradiance.calc_rn

        if not os.access(path, os.R_OK):
            wx.MessageBox("Could not read the specified file", 
                    self.app.title, wx.OK|wx.ICON_ERROR, self)
            return

        # Load the data, set the parameters
        try:
            d = Dataset(path, self.Input.GetFields(), self.Input.GetTrim(), 
                    self.Site.getvalues(), self.Veg.getvalues())
        # We already warn the user about these, so don't raise them - just fail
        # to run the dataset
        except InsufficientTrimError:
            wx.MessageBox("Some of the data was the wrong type - is the number"
                    + "of lines to trim from the input set correctly?",
                    self.app.title,
                    wx.OK|wx.ICON_ERROR,
                    self)
            return
        # Set up the calculation changes
        d.par_r = par_r
        d.rn = rn

        try:
            r = ResultsWindow(self, d, self.recent_dir, len(self.results_windows) + 1)
            self.results_windows.append(r)
            def f(evt):
                self.results_windows.remove(r)
                evt.Skip()
            r.Bind(wx.EVT_CLOSE, f)
        except InvalidFieldCountError:
            wx.MessageBox("Number of fields in the input file does not match "
                    + "the number of fields selected!",
                    self.app.title,
                    wx.OK|wx.ICON_ERROR,
                    self)
            return
        r.Show()
