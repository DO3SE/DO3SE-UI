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
