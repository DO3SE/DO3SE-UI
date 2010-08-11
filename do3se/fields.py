import wx

from do3se.util.ordereddict import OrderedDict

class Field:
    def __init__(self, root, name):
        self.root = root
        self.name = name

    def get_value(self):
        pass

    def set_value(self, value):
        pass

    def create_label(self, parent):
        return wx.StaticText(parent, label=self.name)

    def create_field(self, parent):
        return wx.TextCtrl(parent)


class FieldGroup:
    def __init__(self, root):
        self.root = root
        self.fields = []

    def append(self, field):
        self.fields.append(field)

    def create_panel(self, parent):
        panel = wx.Panel(parent)
        panel.SetSizer(wx.BoxSizer(wx.VERTICAL))
        fgs = wx.FlexGridSizer(cols=2, vgap=5, hgap=5)
        panel.GetSizer().Add(fgs, 0, wx.EXPAND|wx.ALL, 5)

        for f in self.fields:
            fgs.Add(f.create_label(panel), 0, wx.ALIGN_CENTER_VERTICAL)
            fgs.Add(f.create_field(panel), 0, wx.ALIGN_CENTER_VERTICAL)

        return panel


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
