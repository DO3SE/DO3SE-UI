import wx
import os

from FloatSpin import FloatSpin
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

        self.site = {}

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


        ### 'Site parameters' tab ###
        pSite = wx.Panel(nbMain)
        nbMain.AddPage(pSite, "Site parameters")
        sSite = wx.BoxSizer(wx.VERTICAL)
        pSite.SetSizer(sSite)
        presetSite = wxext.PresetChooser(pSite)
        presetSite.SetPresets(app.config['preset.site'])
        def f():
            app.config['preset.site'] = presetSite.GetPresets()
            app.config.sync()
        presetSite.post_update = f
        sSite.Add(presetSite, 0, wx.ALL|wx.EXPAND, 6)
        sSiteParams = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sSiteParams.AddGrowableCol(0)
        sSiteParams.AddGrowableCol(1)
        sSite.Add(sSiteParams, 0, wx.ALL|wx.EXPAND, 6)
        
        # Location parameters
        sbLocation = wx.StaticBox(pSite, label="Location")
        sbsLocation = wx.StaticBoxSizer(sbLocation, wx.VERTICAL)
        sSiteParams.Add(sbsLocation, 0, wx.EXPAND)
        fgsLocation = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sbsLocation.Add(fgsLocation, 1, wx.EXPAND|wx.ALL, 6)
        fgsLocation.Add(wx.StaticText(pSite, label="Latitude"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['lat'] = FloatSpin(pSite, value=45.0, 
                min_val=-90.0, max_val=90.0, increment=0.1, digits=3)
        fgsLocation.Add(self.site['lat'], 0)
        fgsLocation.Add(wx.StaticText(pSite, label="Longitude"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['lon'] = FloatSpin(pSite, value=0.0,
                min_val=-180.0, max_val=180.0, increment=0.1, digits=3)
        fgsLocation.Add(self.site['lon'], 0)
        fgsLocation.Add(wx.StaticText(pSite, label="Elevation"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['elev'] = wx.SpinCtrl(pSite, min=-100, max=5000, initial=0)
        fgsLocation.Add(self.site['elev'], 0)

        # Measurement heights
        sbHeights = wx.StaticBox(pSite, label="Measurement heights")
        sbsHeights = wx.StaticBoxSizer(sbHeights, wx.VERTICAL)
        sSiteParams.Add(sbsHeights, 0, wx.EXPAND)
        fgsHeights = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sbsHeights.Add(fgsHeights, 1, wx.EXPAND|wx.ALL, 6)
        fgsHeights.Add(wx.StaticText(pSite, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['o3zr'] = wx.SpinCtrl(pSite, min=1, max=200, initial=25)
        fgsHeights.Add(self.site['o3zr'], 0)
        fgsHeights.Add(wx.StaticText(pSite, label="Meteorlogical data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['uzr'] = wx.SpinCtrl(pSite, min=1, max=200, initial=25)
        fgsHeights.Add(self.site['uzr'], 0)
        fgsHeights.Add(wx.StaticText(pSite, label="Other data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['xzr'] = wx.SpinCtrl(pSite, min=1, max=200, initial=25)
        fgsHeights.Add(self.site['xzr'], 0)

        # Soil properties
        sbsSoil = wx.StaticBoxSizer(wx.StaticBox(pSite, label="Soil"), wx.VERTICAL)
        sSiteParams.Add(sbsSoil, 0, wx.EXPAND)
        fgsSoil = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sbsSoil.Add(fgsSoil, 1, wx.EXPAND|wx.ALL, 6)
        fgsSoil.Add(wx.StaticText(pSite, label="Texture"), 
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['soil_tex'] = wx.Choice(pSite, choices=['Fine', 'Medium', 'Coarse'])
        self.site['soil_tex'].SetStringSelection('Medium')
        fgsSoil.Add(self.site['soil_tex'], 0)
        fgsSoil.Add(wx.StaticText(pSite, label="Rsoil"),
                0, wx.ALIGN_CENTER_VERTICAL)
        self.site['rsoil'] = wx.SpinCtrl(pSite, min=1, max=1000, initial=200)
        fgsSoil.Add(self.site['rsoil'], 0)

        # Canopy heights
        sbCanopies = wx.StaticBox(pSite, label="Canopy heights")
        sbsCanopies = wx.StaticBoxSizer(sbCanopies, wx.VERTICAL)
        sSiteParams.Add(sbsCanopies, 0, wx.EXPAND)
        fgsCanopies = wx.FlexGridSizer(cols=2, vgap=6, hgap=6)
        sbsCanopies.Add(fgsCanopies, 1, wx.EXPAND|wx.ALL, 6)
        fgsCanopies.Add(wx.StaticText(pSite, label="Ozone data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteO3Canopy = wx.BoxSizer(wx.HORIZONTAL)
        fgsCanopies.Add(sSiteO3Canopy, 0)
        self.site['o3_h'] = wx.SpinCtrl(pSite, min=1, max=200, initial=25)
        sSiteO3Canopy.Add(self.site['o3_h'], 0, wx.RIGHT, 6)
        self.site['o3_h_copy'] = wx.CheckBox(pSite, label="Same as target canopy")
        sSiteO3Canopy.Add(self.site['o3_h_copy'], 0)
        self.site['o3_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.site['o3_h'].Enable(not self.site['o3_h_copy'].IsChecked()),
                self.site['o3_h_copy'])
        fgsCanopies.Add(wx.StaticText(pSite, label="Meteorlogical data"),
                0, wx.ALIGN_CENTER_VERTICAL)
        sSiteMetCanopy = wx.BoxSizer(wx.HORIZONTAL)
        fgsCanopies.Add(sSiteMetCanopy, 0)
        self.site['u_h'] = wx.SpinCtrl(pSite, min=1, max=200, initial=25)
        sSiteMetCanopy.Add(self.site['u_h'], 0, wx.RIGHT, 6)
        self.site['u_h_copy'] = wx.CheckBox(pSite, label="Same as target canopy")
        sSiteMetCanopy.Add(self.site['u_h_copy'], 0)
        self.site['u_h_copy'].Bind(
                wx.EVT_CHECKBOX,
                lambda evt: self.site['u_h'].Enable(not self.site['u_h_copy'].IsChecked()),
                self.site['u_h_copy'])

        def f():
            return {
                'lat'       : float(self.site['lat'].GetValue()),
                'lon'       : float(self.site['lon'].GetValue()),
                'elev'      : float(self.site['elev'].GetValue()),
                'o3zr'      : float(self.site['o3zr'].GetValue()),
                'uzr'       : float(self.site['uzr'].GetValue()),
                'xzr'       : float(self.site['xzr'].GetValue()),
                'o3_h'      : float(self.site['o3_h'].GetValue()),
                'u_h'       : float(self.site['u_h'].GetValue()),
                'o3_h_copy' : self.site['o3_h_copy'].GetValue(),
                'u_h_copy' : self.site['u_h_copy'].GetValue(),
                'rsoil'     : float(self.site['rsoil'].GetValue()),
                'soil_a'    : {'Coarse': -4.0, 'Medium': -5.5, 'Fine': -7.0}
                                [self.site['soil_tex'].GetStringSelection()],
                'soil_b'    : {'Coarse': -2.3, 'Medium': -3.3, 'Fine': -5.4}
                                [self.site['soil_tex'].GetStringSelection()],
                'soil_bd'   : 1.3,
                'fc_m'      : 0.193,
            }
        presetSite.getvalues = f
        def f(v):
            self.site['lat'].SetValue(v['lat'])
            self.site['lon'].SetValue(v['lon'])
            self.site['elev'].SetValue(v['elev'])
            self.site['o3zr'].SetValue(v['o3zr'])
            self.site['uzr'].SetValue(v['uzr'])
            self.site['xzr'].SetValue(v['xzr'])
            self.site['o3_h'].SetValue(v['o3_h'])
            self.site['u_h'].SetValue(v['u_h'])
            self.site['o3_h_copy'].SetValue(v['o3_h_copy'])
            self.site['u_h_copy'].SetValue(v['u_h_copy'])
            self.site['soil_tex'].SetStringSelection(
                {-4.0: 'Coarse', -5.5: 'Medium', -7.0: 'Fine'}[v['soil_a']]
            )
            self.site['rsoil'].SetValue(v['rsoil'])
            self.site['o3_h'].Enable(not self.site['o3_h_copy'].IsChecked())
            self.site['u_h'].Enable(not self.site['u_h_copy'].IsChecked())
        presetSite.setvalues = f
            

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
        sHeaders = wx.BoxSizer(wx.HORIZONTAL)
        sOutput.Add(sHeaders, 0, wx.ALL|wx.ALIGN_LEFT, 6)
        self.chkOutputHeaders = wx.CheckBox(pOutput, label="Include column headers")
        sHeaders.Add(self.chkOutputHeaders, 0, wx.EXPAND)
        self.chkOutputHeaders.SetValue(True)
        # Preset manager get-/setvalues callbacks
        def f():
            return {
                'fields': maps.outputs.rmap(self.slOutputs.GetSelection()),
                'headers': self.chkOutputHeaders.GetValue()
            }
        presetOutput.getvalues = f
        def f(v):
            self.slOutputs.SetSelection(maps.outputs.map(v['fields']))
            self.chkOutputHeaders.SetValue(v['headers'])
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
        
