# coding: utf-8
import os.path
import logging
_log = logging.getLogger('do3se.ui')

import wx
import wx.html
import wx.lib.plot
import wx.lib.delayedresult

import wxext
import model
import ui_xrc
import dialogs
import fields
import fieldgroups
from project import Project
from dataset import Dataset, DatasetError
from resultswindow import ResultsWindow
# from help_about import DO3SEAbout TODO: This module is missing


_intro_text = u"""
<h2>DO<sub>3</sub>SE model user interface</h2>

To start using the model, click the "New project" button at the bottom.  To
use an existing project either click it in the "Recent projects" list and click
"Open selected", or click "Open other..." and locate your project (.do3se) file.

<h5>Background</h5>
<p>
DO<sub>3</sub>SE (Deposition of Ozone for Stomatal Exchange) is a dry deposition
model designed to estimate the total and stomatal deposition (or flux) of ozone
(O<sub>3</sub>) to selected European land-cover types and plant species.
DO<sub>3</sub>SE has been developed to estimate the risk of O<sub>3</sub> damage
to European vegetation and is capable of providing flux-modelling estimates
according to UNECE LRTAP (Long-Range Transboundary Air Pollution) methodologies
for effects-based risk assessment.  An almost identical version of
DO<sub>3</sub>SE has been embedded in the EMEP photochemical model to provide
estimates of total O<sub>3</sub> deposition and O<sub>3</sub> risk providing an
opportunity to formulate effects-based O<sub>3 precursor emission
reduction strategies for Europe.
</p>

<p align="center">
<img src="memory:resources/resistance.png" />
</p>

<p>
DO<sub>3</sub>SE assumes that the key resistances to O<sub>3</sub> deposition
from an O<sub>3</sub> concentration (C<sub>O3</sub>) at some reference height in
the atmosphere to the ground surface are: the aerodynamic resistance
(R<sub>a</sub>), the quasi-laminar sub-layer resistance (R<sub>b</sub>) above
the canopy, and the surface resistance (R<sub>sur</sub>).  R<sub>sur</sub>
comprises two resistance paths in series; the stomatal and non-stomatal
resistance.  The latter represents within canopy aerodynamic resistance
(R<sub>inc</sub>) and subsequent soil resistance to decomposition at the soil
surface (R<sub>soil</sub>) which encompasses features such as leaf litter and
ground vegetation under forest canopies; as well as resistance to adsorption to
the external plant parts (R<sub>ext</sub>) including cuticle, bark etc.  The
stomatal resistance term (R<sub>sto</sub>) determines the resistance to
O<sub>3</sub> uptake by the vegetation and hence is relevant for risk assessment
since it is via the stomates that O<sub>3</sub> enters and causes damage to
vegetation.
</p>

<p>
This interfaced version of the model (DO3SE_INTv2.0) is provided for users to
estimate total and stomatal O<sub>3</sub> flux on a site-specific basis
according to local meteorological and O<sub>3</sub> concentration data.
Default parameterisation is provided for certain cover-types and species though
users have the option of using their own local parameterisation.  The model
provides estimates of key deposition parameters including: total deposition
(F<sub>tot</sub>), deposition velocity (V<sub>g</sub>), stomatal conductance
(g<sub>sto</sub>) and accumulated leaf-level stomtal flux above a threshold
(PODy).
</p>

<p>
Full referenced documentation of the DO<sub>3</sub>SE model and a DO3SE_INTv2.0
user manual is provided with this model interface.
</p>

<p>
<b>For any comments or queries please contact either Patrick Büker
(patrick.bueker@york.ac.uk) or Lisa Emberson (l.emberson@york.ac.uk).</b>
</p>

<h5>Acknowledgements</h5>
<p>
The development of this interface has been made possible through funding
provided by the UK Department of Environment, Food and Rural Affairs (Defra) and
through institutional support provided to the Stockholm Environment Institute
from the Swedish International Development Agency (Sida).
</p>
"""


class MainWindow(ui_xrc.xrcframe_mainwindow):
    def __init__(self, app):
        super(MainWindow, self).__init__(None)

        self.frame.SetSize((500,500))
        self.app = app
        self.html_about.SetPage(_intro_text)
        self.list_recent.Clear()
        for p in reversed(self.app.config.data['recent_projects']):
            self.list_recent.Append(p)

    def Show(self):
        # Overriden Show() as part of fixing preframe issue
        self.frame.Show()

    def OnListbox_list_recent(self, evt):
        enabled = self.list_recent.GetSelection() != wx.NOT_FOUND
        self.btn_open_selected.Enable(enabled)

    def OnListbox_dclick_list_recent(self, evt):
        self.OnButton_btn_open_selected(evt)

    def OnButton_btn_new(self, evt):
        w = ProjectWindow(self.app, None)
        w.Show()
        self.Close()

    def OnButton_btn_open_selected(self, evt):
        filename = self.list_recent.GetStringSelection()
        w = ProjectWindow(self.app, filename)
        w.Show()
        self.Close()

    def OnButton_btn_open_other(self, evt):
        filename = dialogs.open_project(self)
        if filename is not None:
            w = ProjectWindow(self.app, filename)
            w.Show()
            self.Close()


class ProjectWindow(ui_xrc.xrcframe_projectwindow):
    ui_specification = (
        ('format', 'Input data format', fieldgroups.InputFormatParams, (), {}),
        ('siteloc', 'Location properties', fieldgroups.SiteLocationParams, (), {}),
        ('meas', 'Measurement data', fieldgroups.MeasurementParams, (), {}),
        ('vegchar', 'Vegetation characteristics', fieldgroups.VegCharParams, (), {}),
        ('vegenv', 'Environmental response', fieldgroups.VegEnvParams, (), {}),
        ('modelopts', 'Model options', fieldgroups.ModelOptionsParams, (), {}),
        ('season', 'Season', fieldgroups.SeasonParams, (), {}),
        ('fphen', 'fphen', fieldgroups.FphenParams, (), {}),
        ('leaf_fphen', 'Leaf fphen', fieldgroups.LeafFphenParams, (), {}),
    )

    def __init__(self, app, projectfile):
        super(ProjectWindow, self).__init__(None)

        self.frame.SetSize((780,780))

        # Add context help button
        _s = self.btn_run.GetContainingSizer()
        _s.PrependSpacer(5)
        self.btn_help = wx.ContextHelpButton(_s.GetContainingWindow())
        _s.Prepend(self.btn_help, 0, wx.EXPAND)

        self.app = app

        # map xrc and ui spec to params
        self.params: FieldCollection = fields.FieldCollection(self.tb_main, self.ui_specification)

        if projectfile is not None and self.app.IsProjectOpen(projectfile):
            _log.warning('Project already open: ' + projectfile)
            projectfile = None
            wx.MessageBox('Project already open, empty project created instead',
                          'Error',
                          wx.OK|wx.ICON_ERROR,
                          self)
        self.project = Project(projectfile, self)

        # assign project data to field groups
        self.params.set_values(self.project.data)
        self.app.windows.add(self)

        # If the project file exists, add it to recent project list
        if self.project.exists():
            self.app.config.add_recent_project(self.project.filename)
            self.app.config.save()

        # Keep track of whether or not there have been changes since last save
        self.unsaved = False
        self.Bind(fields.EVT_VALUE_CHANGED, self.OnFieldUpdate)

        self.UpdateTitle()
        self.UpdateErrors()

    def Show(self):
        # Overriden Show() as part of precreate issue
        self.frame.Show()

    def UpdateTitle(self):
        title = self.app.GetAppName()
        if self.unsaved:
            title = '*' + title
        if self.project.filename is not None:
            title += ' - ' + os.path.basename(self.project.filename)
        self.SetTitle(title)

    def UpdateErrors(self):
        errors = self.params.validate()
        self.list_errors.Clear()
        if errors:
            self.list_errors.InsertItems(list(map(str, errors)), 0)
        if len(errors) == 0:
            self.btn_run.Enable(True)
            self.btn_errors.SetLabel('No errors')
            self.btn_errors.SetForegroundColour(wx.NullColour)
        else:
            self.btn_run.Enable(False)
            self.btn_errors.SetLabel('%d errors (click for more information)' % (len(errors),))
            self.btn_errors.SetForegroundColour(wx.RED)
        self.btn_errors.GetContainingSizer().Layout()

    @wxext.autoeventskip
    def OnFieldUpdate(self, evt):
        _log.debug('Something was updated: ' + str(evt))
        if not self.unsaved:
            self.unsaved = True
            self.UpdateTitle()
        self.UpdateErrors()

    def OnClose(self, evt):
        really_close = False
        if self.unsaved:
            response = wx.MessageBox('Project has unsaved changes.  Save?',
                                     'Unsaved changes',
                                     wx.YES_NO|wx.CANCEL|wx.ICON_EXCLAMATION,
                                     self)
            if response == wx.NO:
                really_close = True
            elif response == wx.YES:
                self.project.data = self.params.get_values()
                if self.project.save():
                    really_close = True
        else:
            really_close = True

        if really_close:
            self.app.windows.remove(self)
            evt.Skip()
        else:
            evt.Veto()


    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()

    def OnButton_btn_run(self, evt):
        """Run project with a data file.

        The user is prompted for a data file to load.  The input data is
        loaded, then the model is run in a separate thread (to maintain UI
        responsiveness) and a results window opened.  During the model run,
        the window is disabled and made modal to ensure there is no risk of
        another concurrent model run.
        """
        filename = dialogs.open_datafile(self)
        if filename is None:
            return

        try:
            d = Dataset(open(filename, 'r'), self.params.get_values(), self)
        except DatasetError as e:
            wx.MessageBox('Error occurred while loading data file: ' + str(e),
                          'Error',
                          wx.OK|wx.ICON_ERROR,
                          self)
            return

        # Function to return to when the model has been run
        def f(dr):
            self.Enable(True)
            self.MakeModal(False)
            w = ResultsWindow(self.app, self, dr.get(), os.path.basename(filename))
            w.Show()

        self.MakeModal(True)
        self.Enable(False)
        wx.lib.delayedresult.startWorker(f, d.run, wargs=[self.prg_progress])

    def OnMenu_wxID_NEW(self, evt):
        w = ProjectWindow(self.app, None)
        w.Show()

    def OnMenu_wxID_OPEN(self, evt):
        filename = dialogs.open_project(self)
        if filename is not None:
            w = ProjectWindow(self.app, filename)
            w.Show()

    def OnMenu_wxID_SAVE(self, evt):
        self.project.data = self.params.get_values()
        if self.project.save():
            self.unsaved = False
            self.UpdateTitle()

    def OnMenu_wxID_SAVEAS(self, evt):
        self.project.data = self.params.get_values()
        if self.project.save(True):
            self.unsaved = False
            self.UpdateTitle()

    def OnMenu_wxID_CLOSE(self, evt):
        self.Close()

    def OnMenu_wxID_EXIT(self, evt):
        self.app.Quit()

    def OnMenu_create_preset(self, evt):
        dialogs.make_preset(self,
                            self.app.config.data['presets'],
                            self.params.get_values().items())
        self.app.config.save()

    def OnMenu_manage_presets(self, evt):
        values = dialogs.apply_preset(self, self.app.config.data['presets'],
                                      self.app.default_presets)
        self.params.set_values(dict(values))

        if len(values) > 0:
            self.OnFieldUpdate(None)
            # Update parts of the UI that depend on field values
            for group in self.params.values():
                newevt = fields.ValueChangedEvent(group.GetId())
                wx.PostEvent(group, newevt)

        # Save the config, in case presets were deleted
        self.app.config.save()

    def OnMenu_open_docs(self, evt):
        import sys
        help_path = sys.executable.split("\\")
        help_path = '\\'.join(help_path[:-1])
        import os
        os.startfile(help_path + '\\DO3SE-UI Help.chm')

    def OnMenu_open_about(self, evt):
        pass
        # TODO: lost DO3SEAbout!
        # dlg = DO3SEAbout(self)
        # dlg.ShowModal()
        # dlg.Destroy()