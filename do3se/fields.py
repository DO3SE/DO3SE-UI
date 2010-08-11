import logging

import wx

import wxext
from util.ordereddict import OrderedDict


class Field:
    def __init__(self, parent, name):
        self.label = wx.StaticText(parent, label=name)
        self.field = wx.TextCtrl(parent)
        self.other = None

    def get_value(self):
        return self.field.GetValue()

    def set_value(self, value):
        self.field.SetValue(value)


class SpinField(Field):
    def __init__(self, parent, name, min=0, max=100, initial=0):
        self.label = wx.StaticText(parent, label=name)
        self.field = wx.SpinCtrl(parent, min=min, max=max, initial=initial)
        self.other = None


class FloatSpinField(Field):
    def __init__(self, parent, name, min=0, max=1, initial=0, step=0.1, digits=2):
        self.label = wx.StaticText(parent, label=name)
        self.field = wxext.FloatSpin(parent, min_val=min, max_val=max, value=initial,
                                     increment=step, digits=digits)
        self.other = None

    def get_value(self):
        return float(self.field.GetValue())


class FieldGroup(OrderedDict, wx.Panel):
    log = logging.getLogger('do3se.fields.FieldGroup')

    def __init__(self, parent):
        OrderedDict.__init__(self)
        wx.Panel.__init__(self, parent)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))
        self.sizer = wx.FlexGridSizer(cols=3, vgap=5, hgap=5)
        self.GetSizer().Add(self.sizer, 0, wx.EXPAND|wx.ALL, 5)

    def get_values(self):
        """Return field group as (key, value) pairs."""
        return ((k, v.get_value()) for k,v in self.iteritems())

    def set_values(self, values):
        """Set field group values from (key, value) pairs."""
        for k,v in values:
            if k not in self:
                self.log.warning('Skipping parameter ' + k)
            else:
                self[k].set_value(v)

    def add(self, key, cls, *args, **kwargs):
        self[key] = cls(self, *args, **kwargs)
        self.sizer.Add(self[key].label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.sizer.Add(self[key].field, 0, wx.ALIGN_CENTER_VERTICAL)
        if self[key].other is None:
            self.sizer.AddSpacer(0)
        else:
            self.sizer.Add(self[key].other, 0, wx.ALIGN_CENTER_VERTICAL)


class Fields:
    def __init__(self):
        self.fieldgroups = OrderedDict()

    def add_group(self, group, name):
        self.fieldgroups[name] = group

    def get_values(self):
        pass

    def set_values(self, values):
        pass

    def add_to_ui(self, book):
        for name, group in self.fieldgroups.iteritems():
            book.AddPage(group.create_panel(book), name)
