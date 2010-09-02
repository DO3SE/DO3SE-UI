# coding: utf-8
import logging
import os.path

import wx
import wx.html

import wxext
import model
import ui_xrc
import dialogs
from fields import *
from project import Project
from util import load_presets


_intro_text = u"""
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
<img src="resources/resistance.png" />
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
O3 uptake by the vegetation and hence is relevant for risk assessment
since it is via the stomates that O<sub>3</sub> enters and causes damage to
vegetation.
</p>

<p>
This interfaced version of the model (DO3SE_INTv1.0) is provided for users to
estimate total and stomatal O3 flux on a site-specific basis
according to local meteorological and O3 concentration data.
Default parameterisation is provided for certain cover-types and species though
users have the option of using their own local parameterisation.  The model
provides estimates of key deposition parameters including: total deposition
(F<sub>tot</sub>), deposition velocity (V<sub>g</sub>), stomatal conductance
(g<sub>sto</sub>) and accumulated leaf-level stomtal flux above a threshold
(AFstY).
</p>

<p>
Full referenced documentation of the DO<sub>3</sub>SE model and a DO3SE_INTv1.0
user manual is provided with this model interface.
</p>

<p>
<b>For any comments or queries please contact either Patrick Büker
(pb25@york.ac.uk) or Lisa Emberson (l.emberson@york.ac.uk).</b>
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
    def __init__(self, app, parent):
        ui_xrc.xrcframe_mainwindow.__init__(self, parent)
        self.app = app
        self.html_about.SetPage(_intro_text)

    def OnListbox_list_recent(self, evt):
        enabled = self.list_recent.GetSelection() != wx.NOT_FOUND
        self.btn_open_selected.Enable(enabled)

    def OnListbox_dclick_list_recent(self, evt):
        self.OnButton_btn_open_selected(evt)

    def OnButton_btn_new(self, evt):
        w = ProjectWindow(self.app, None)
        w.Show()
        self.Close()


class InputFormat(FieldGroup):
    def __init__(self, fc, parent):
        FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

        self.input_fields = wxext.ListSelectCtrl(self)
        self.input_fields.SetAvailable([(x['long'], x['variable']) for x in model.input_fields])
        self.GetSizer().Add(self.input_fields, 1, wx.EXPAND|wx.ALL, 5)

        self.input_trim = SpinField(self, 0, 10, 0)
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.GetSizer().Add(s, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        s.Add(wx.StaticText(self, label='Number of lines to trim from ' + \
                            'beginning of file (e.g. for column headers'),
              0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        s.Add(self.input_trim.field, 0, wx.EXPAND)

    def get_values(self):
        return OrderedDict((('input_fields', [b for a,b in self.input_fields.GetSelectionWithData()]),
                            ('input_trim', self.input_trim.get_value())))

    def set_values(self, values):
        if 'input_fields' in values:
            self.input_fields.SetSelection([model.input_field_map[x]['long'] for x in values['input_fields']])
        if 'input_trim' in values:
            self.input_trim.set_value(values['input_trim'])


class ProjectWindow(ui_xrc.xrcframe_projectwindow):
    log = logging.getLogger('do3se.projectwindow')
    ui_specification = (
        ('format', 'Input data format', InputFormat, (), {}),
        ('siteloc', 'Location properties', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('siteloc')}),
        ('meas', 'Measurement data', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('meas')}),
        ('vegchar', 'Vegetation characteristics', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('vegchar')}),
        ('vegenv', 'Environmental response', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('vegenv')}),
        ('modelopts', 'Model options', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('modelopts')}),
        ('unsorted', 'UNSORTED', SimpleFieldGroup, (),
            {'fields': model.parameters_by_group('unsorted')}),
    )

    def __init__(self, app, projectfile):
        ui_xrc.xrcframe_projectwindow.__init__(self, None)
        self.SetSize((780,550))
        # TODO: only enable Run button when no errors
        self.btn_run.Enable(True)
        
        self.app = app
        self.params = FieldCollection(self.tb_main, self.ui_specification)
        self.project = Project(projectfile, self)
        self.params.set_values(self.project.data)

        # Keep track of whether or not there have been changes since last save
        self.unsaved = False
        self.Bind(wx.EVT_TEXT, self.OnFieldUpdate)
        self.Bind(wx.EVT_SPINCTRL, self.OnFieldUpdate)
        self.Bind(wx.EVT_CHOICE, self.OnFieldUpdate)
        self.Bind(wx.EVT_CHECKBOX, self.OnFieldUpdate)
        self.Bind(wx.EVT_LISTBOX, self.OnFieldUpdate)
        self.UpdateTitle()

    def UpdateTitle(self):
        title = 'DO3SE'
        if self.unsaved:
            title = '*' + title
        if self.project.filename is not None:
            title += ' - ' + os.path.basename(self.project.filename)
        self.SetTitle(title)

    def OnFieldUpdate(self, evt):
        self.log.debug('Something was updated: ' + str(evt))
        if not self.unsaved:
            self.unsaved = True
            self.UpdateTitle()
        if evt is not None:
            evt.Skip()

    def OnClose(self, evt):
        evt.Skip()

    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()

    def OnButton_btn_run(self, evt):
        print self.params.get_values()

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
        # Save the config, in case presets were deleted
        self.app.config.save()
