import logging

import wx

import wxext
from util.ordereddict import OrderedDict


class Field:
    def __init__(self, parent, name, *args, **kwargs):
        self.label = wx.StaticText(parent, label=name)
        self.field = None
        self.other = None

        self.create_ui(parent, *args, **kwargs)

    def create_ui(self, parent, *args, **kwargs):
        raise NotImplementedError

    def get_value(self):
        return self.field.GetValue()

    def set_value(self, value):
        self.field.SetValue(value)


class TextField(Field):
    def create_ui(self, parent, initial=''):
        self.field = wx.TextCtrl(parent)
        self.field.SetValue(initial)


class SpinField(Field):
    def create_ui(self, parent, min=0, max=100, initial=0):
        self.field = wx.SpinCtrl(parent, min=min, max=max, initial=initial)


class FloatSpinField(Field):
    def create_ui(self, parent, min=0, max=1, initial=0, step=0.1, digits=2):
        self.field = wxext.FloatSpin(parent, min_val=min, max_val=max, value=initial,
                                     increment=step, digits=digits)

    def get_value(self):
        return float(self.field.GetValue())


class FieldGroup(OrderedDict, wx.Panel):
    log = logging.getLogger('do3se.fields.FieldGroup')

    def __init__(self, fc, parent):
        OrderedDict.__init__(self)
        wx.Panel.__init__(self, parent)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.sizer = wx.FlexGridSizer(cols=3, vgap=5, hgap=5)
        self.GetSizer().Add(self.sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.fc = fc

    def get_values(self):
        """Return field group as (key, value) pairs."""
        return ((k, v.get_value()) for k,v in self.iteritems())

    def set_values(self, values):
        """Set field group values from (key, value) pairs."""
        for k,v in values:
            if k in self:
                self[k].set_value(v)

    def add(self, key, cls, *args, **kwargs):
        self[key] = cls(self, *args, **kwargs)
        self.sizer.Add(self[key].label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self[key].field, 0, wx.ALIGN_CENTER_VERTICAL)
        if self[key].other is None:
            self.sizer.AddSpacer(0)
        else:
            self.sizer.Add(self[key].other, 0, wx.ALIGN_CENTER_VERTICAL)


class FieldCollection(OrderedDict):
    def __init__(self, treebook):
        OrderedDict.__init__(self)
        self.treebook = treebook

    def add_group(self, key, name, cls=FieldGroup, *args, **kwargs):
        self[key] = cls(self, self.treebook, *args, **kwargs)
        self.treebook.AddPage(self[key], name)
        return self[key]

    def get_values(self):
        values = []
        for group in self.itervalues():
            values.extend(group.get_values())
        return values

    def set_values(self, values):
        for group in self.itervalues():
            group.set_values(values)


_parameters_ui = (
    ('format', 'Input data format', FieldGroup, (), {}, ()),
    ('siteloc', 'Site location', FieldGroup, (), {}, (
        ('lat', FloatSpinField, ('Latitude (degrees North)', -90, 90, 50, 0.1, 3), {}),
        ('lon', FloatSpinField, ('Longitude (degrees East)', -180, 180, 0, 0.1, 3), {}),
        ('elev', SpinField, ('Elevation (m.a.s.l.)', -100, 5000, 0), {}),
    )),
    ('meas', 'Measurement data', FieldGroup, (), {}, (
        ('o3zr', SpinField, ('Ozone concentration measurement height (m)', 1, 200, 25), {}),
        ('uzr', SpinField, ('Wind speed measurement height (m)', 1, 200, 25), {}),
        ('d_meas', FloatSpinField, ('Soil water measurement depth (m)', 0.1, 2, 0.5, 0.1, 1), {}),
    )),
    ('vegchar', 'Vegetation characteristics', FieldGroup, (), {}, (
        ('h', FloatSpinField, ('Canopy height (h, m)', 0.1, 100, 25, 0.1, 1), {}),
        ('root', FloatSpinField, ('Root depth (root, m)', 0.1, 10, 1.2, 0.1, 1), {}),
        ('lm', FloatSpinField, ('Leaf dimension (Lm, m)', 0.01, 1, 0.05, 0.01, 2), {}),
        ('albedo', FloatSpinField, ('Albedo', 0.01, 0.99, 0.12, 0.01, 2), {}),
        ('gmax', SpinField, ('gmax', 1, 10000, 148), {}),
        ('gmorph', FloatSpinField, ('gmorph', 0.01, 1, 1, 0.01, 2), {}),
        ('fmin', FloatSpinField, ('fmin', 0.01, 0.99, 0.13, 0.01, 2), {}),
        ('rext', SpinField, ('External plant cuticle resistance (Rext, s/m)', 0, 20000, 2500), {}),
        ('y', FloatSpinField, ('Threshold Y for AFstY (nmol/m2/s)', 0.1, 100, 1.6, 0.1, 1), {}),
    )),
    ('vegenv', 'Environmental response', FieldGroup, (), {}, (
        ('f_lightfac', FloatSpinField, ('light_a', 0.001, 0.999, 0.006, 0.001, 3), {}),
        ('t_min', SpinField, (u'Minimum temperature (T_min, \u00b0C)', -10, 100, 0), {}),
        ('t_opt', SpinField, (u'Optimum temperature (T_opt, \u00b0C)', -10, 100, 21), {}),
        ('t_max', SpinField, (u'Maximum temperature (T_max, \u00b0C)', -10, 100, 35), {}),
        ('vpd_max', FloatSpinField, ('VPD for max. g (VPD_max, kPa)', 0, 100, 1, 0.01, 2), {}),
        ('vpd_min', FloatSpinField, ('VPD for min. g (VPD_min, kPa)', 0, 100, 3.25, 0.01, 2), {}),
        ('vpd_crit', FloatSpinField, ('Critical daily VPD sum (VPD_crit, kPa)', 0, 1000, 1000, 1, 1), {}),
        ('swp_min', FloatSpinField, ('SWP for min. g (SWP_min, ???)', -6, 0, -1.25, 0.01, 2), {}),
        ('swp_max', FloatSpinField, ('SWP for max. g (SWP_max, ???)', -6, 0, -0.05, 0.01, 2), {}),
    )),
)


def create_parameters_ui(parent):
    fc = FieldCollection(parent)
    for gkey, gname, gcls, gargs, gkwargs, fields in _parameters_ui:
        fg = fc.add_group(gkey, gname, gcls, *gargs, **gkwargs)
        for key, cls, args, kwargs in fields:
            fg.add(key, cls, *args, **kwargs)
    return fc
