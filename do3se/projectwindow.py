import logging

import wx

import wxext
import ui_xrc
import model
from fields import *


class InputFormat(FieldGroup):
    def __init__(self, fc, parent):
        FieldGroup.__init__(self, fc, parent)

        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

        self.input_fields = wxext.ListSelectCtrl(self)
        self.input_fields.SetAvailable([(x['long'], x['variable']) for x in model.input_fields])
        self.GetSizer().Add(self.input_fields, 1, wx.EXPAND|wx.ALL, 5)

        self.input_trim = SpinField(self, 'Number of lines to trim from ' + \
                'beginning of file (e.g. for column headers', 0, 10, 0)
        s = wx.BoxSizer(wx.HORIZONTAL)
        self.GetSizer().Add(s, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        s.Add(self.input_trim.label, 0, wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        s.Add(self.input_trim.field, 0, wx.EXPAND)

    def get_values(self):
        return OrderedDict(input_fields=[b for a,b in self.input_fields.GetSelectionWithData()],
                           input_trim=self.input_trim.get_value())

    def set_values(self, values):
        if 'input_fields' in values:
            self.input_fields.SetSelection([model.input_field_map[x]['long'] for x in values['input_fields']])
        if 'input_trim' in values:
            self.input_trim.set_value(values['input_trim'])


class ProjectWindow(ui_xrc.xrcframe_projectwindow):
    log = logging.getLogger('do3se.ui.projectwindow')

    def __init__(self, projectfile):
        ui_xrc.xrcframe_projectwindow.__init__(self, None)
        self.SetSize((780,550))
        self.btn_run.Enable(True)
        
        if projectfile:
            self.log.info("Opening project " + projectfile)
        else:
            self.log.info("Creating new project")

        self.params = FieldCollection(self.tb_main, _parameters_ui)

    def OnClose(self, evt):
        evt.Skip()

    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()

    def OnButton_btn_run(self, evt):
        print self.params.get_values()

    def OnButton_btn_close(self, evt):
        self.Close()


_parameters_ui = (
    ('format', 'Input data format', InputFormat, (), {}),
    ('siteloc', 'Location properties', SimpleFieldGroup, (), {'fields': (
        ('lat', FloatSpinField, ('Latitude (degrees North)', -90, 90, 50, 0.1, 3), {}),
        ('lon', FloatSpinField, ('Longitude (degrees East)', -180, 180, 0, 0.1, 3), {}),
        ('elev', SpinField, ('Elevation (m.a.s.l.)', -100, 5000, 0), {}),
        ('soil_tex', ChoiceField, ('Soil texture', model.soil_class_map, model.default_soil_class), {}),
        ('rsoil', SpinField, ('Rsoil', 1, 1000, 200), {}),
    )}),
    ('meas', 'Measurement data', SimpleFieldGroup, (), {'fields': (
        ('o3zr', SpinField, ('O3 measurement height (m)', 1, 200, 25), {}),
        ('o3_h', disableable(FloatSpinField, 'Same as target canopy'),
            ('O3 measurement canopy height (m)', 0.1, 100, 25, 0.1, 1), {}),
        ('uzr', SpinField, ('Wind speed measurement height (m)', 1, 200, 25), {}),
        ('u_h', disableable(FloatSpinField, 'Same as target canopy'),
            ('Wind speed measurement canopy height (m)', 0.1, 100, 25, 0.1, 1), {}),
        ('d_meas', FloatSpinField, ('Soil water measurement depth (m)', 0.1, 2, 0.5, 0.1, 1), {}),
    )}),
    ('vegchar', 'Vegetation characteristics', SimpleFieldGroup, (), {'fields': (
        ('h', FloatSpinField, ('Canopy height (h, m)', 0.1, 100, 25, 0.1, 1), {}),
        ('root', FloatSpinField, ('Root depth (root, m)', 0.1, 10, 1.2, 0.1, 1), {}),
        ('lm', FloatSpinField, ('Leaf dimension (Lm, m)', 0.01, 1, 0.05, 0.01, 2), {}),
        ('albedo', FloatSpinField, ('Albedo', 0.01, 0.99, 0.12, 0.01, 2), {}),
        ('gmax', SpinField, ('gmax', 1, 10000, 148), {}),
        ('gmorph', FloatSpinField, ('gmorph', 0.01, 1, 1, 0.01, 2), {}),
        ('fmin', FloatSpinField, ('fmin', 0.01, 0.99, 0.13, 0.01, 2), {}),
        ('rext', SpinField, ('External plant cuticle resistance (Rext, s/m)', 0, 20000, 2500), {}),
        ('y', FloatSpinField, ('Threshold Y for AFstY (nmol/m2/s)', 0.1, 100, 1.6, 0.1, 1), {}),
    )}),
    ('vegenv', 'Environmental response', SimpleFieldGroup, (), {'fields': (
        ('f_lightfac', FloatSpinField, ('light_a', 0.001, 0.999, 0.006, 0.001, 3), {}),
        ('t_min', SpinField, (u'Minimum temperature (T_min, \u00b0C)', -10, 100, 0), {}),
        ('t_opt', SpinField, (u'Optimum temperature (T_opt, \u00b0C)', -10, 100, 21), {}),
        ('t_max', SpinField, (u'Maximum temperature (T_max, \u00b0C)', -10, 100, 35), {}),
        ('vpd_max', FloatSpinField, ('VPD for max. g (VPD_max, kPa)', 0, 100, 1, 0.01, 2), {}),
        ('vpd_min', FloatSpinField, ('VPD for min. g (VPD_min, kPa)', 0, 100, 3.25, 0.01, 2), {}),
        ('vpd_crit', FloatSpinField, ('Critical daily VPD sum (VPD_crit, kPa)', 0, 1000, 1000, 1, 1), {}),
        ('swp_min', FloatSpinField, ('SWP for min. g (SWP_min, ???)', -6, 0, -1.25, 0.01, 2), {}),
        ('swp_max', FloatSpinField, ('SWP for max. g (SWP_max, ???)', -6, 0, -0.05, 0.01, 2), {}),
    )}),
    ('modelopts', 'Model options', SimpleFieldGroup, (), {'fields': (
        ('fo3', ChoiceField, ('fO3 calculation', model.fO3_calc_map, model.default_fO3_calc), {}),
        ('fxwp', ChoiceField, ('Soil water influence on Gsto', model.fXWP_calc_map, model.default_fXWP_calc), {}),
        ('lwp', ChoiceField, ('LWP calculation', model.LWP_calc_map, model.default_LWP_calc), {}),
        ('fswp', ChoiceField, ('fSWP calculation', model.fSWP_calc_map, model.default_fSWP_calc), {}),
    )}),
    ('unsorted', 'UNSORTED', SimpleFieldGroup, (), {'fields': (
        ('sgs', SpinField, ('Start of growing season (SGS, day of year)', 1, 365, 121), {}),
        ('egs', SpinField, ('End of growing season (EGS, day of year)', 1, 365, 273), {}),

        ('lai_a', FloatSpinField, ('LAI at SGS (LAI_a, m2/m2)', 0, 20, 0, 0.1, 1), {}),
        ('lai_b', FloatSpinField, ('First mid-season LAI (LAI_b, m2/m2)', 0, 20, 4, 0.1, 1), {}),
        ('lai_c', FloatSpinField, ('Second mid-season LAI (LAI_c, m2/m2)', 0, 20, 4, 0.1, 1), {}),
        ('lai_d', FloatSpinField, ('LAI at EGS (LAI_d, m2/m2)', 0, 20, 0, 0.1, 1), {}),
        ('lai_1', SpinField, ('Period from LAI_a to LAI_b (LAI_1, days)', 1, 100, 30), {}),
        ('lai_2', SpinField, ('Period from LAI_c to LAI_d (LAI_2, days)', 1, 100, 30), {}),
        ('sai', ChoiceField, ('SAI calculation', model.SAI_calc_map, model.default_SAI_calc), {}),

        ('fphen_a', FloatSpinField, ('Fphen at SGS (fphen_a)', 0, 1, 0, 0.1, 1), {}),
        ('fphen_b', FloatSpinField, ('First mid-season Fphen (fphen_b)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_c', FloatSpinField, ('Second mid-season Fphen (fphen_c)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_d', FloatSpinField, ('Third mid-season Fphen (fphen_d)', 0, 1, 1, 0.1, 1), {}),
        ('fphen_e', FloatSpinField, ('Fphen at EGS (fphen_e)', 0, 1, 0, 0.1, 1), {}),
        ('fphen_1', SpinField, ('Period from fphen_a to fphen_b (fphen_1, days)', 0, 200, 15), {}),
        ('fphen_lima', SpinField, ('Start of SWP limitation (fphen_limA, day of year)', 0, 365, 0), {}),
        ('fphen_2', SpinField, ('Period from fphen_b to fphen_c (fphen_2, days)', 0, 200, 1), {}),
        ('fphen_3', SpinField, ('Period from fphen_c to fphen_d (fphen_3, days)', 0, 200, 1), {}),
        ('fphen_limb', SpinField, ('End of SWP limitation (fphen_limB, day of year)', 0, 365, 0), {}),
        ('fphen_4', SpinField, ('Period from fphen_d to fphen_e (fphen_4, days)', 0, 200, 20), {}),

        ('leaf_fphen', ChoiceField, ('Leaf fphen calculation', model.leaf_fphen_calc_map, model.default_leaf_fphen_calc), {}),
        ('astart', SpinField, ('Start of O3 accumulation (Astart, day of year)', 1, 365, 153), {}),
        ('aend', SpinField, ('End of O3 accumulation (Aend, day of year)', 1, 365, 208), {}),
        ('leaf_fphen_a', FloatSpinField, ('Leaf fphen at Astart (leaf_fphen_a)', 0, 1, 0, 0.1, 1), {}),
        ('leaf_fphen_b', FloatSpinField, ('Leaf fphen mid-season (leaf_fphen_b)', 0, 1, 1, 0.1, 1), {}),
        ('leaf_fphen_c', FloatSpinField, ('Leaf fphen at Aend (leaf_fphen_c)', 0, 1, 0, 0.1, 1), {}),
        ('leaf_fphen_1', SpinField, ('Period from leaf_fphen_a to leaf_fphen_b (days)', 0, 300, 15), {}),
        ('leaf_fphen_2', SpinField, ('Period from leaf_fphen_b to leaf_fphen_c (days)', 0, 300, 30), {}),
    )}),
)
