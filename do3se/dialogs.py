import os.path
import sys

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

import model


#: Default/suggested file extension for project files
FILE_EXTENSION = '.do3se'
#: Wildcard string for :class:`wx.FileDialog`
FILE_WILDCARD = 'DO3SE project files (*%s)|*%s|All (*.*)|*.*' % (FILE_EXTENSION, FILE_EXTENSION)


def save_project(parent, default='project'+FILE_EXTENSION):
    """Get a valid project filename for saving a project.

    Returns either a valid file path to save the project as, or None if the user
    cancelled.  *parent* is used as the window the dialog is associated with,
    and *default* is a default file path to use.
    """
    fd = wx.FileDialog(parent, message='Save project',
                       defaultDir=os.path.dirname(default),
                       defaultFile=os.path.basename(default),
                       wildcard=FILE_WILDCARD,
                       style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)

    if fd.ShowModal() == wx.ID_OK:
        return fd.GetPath()
    else:
        return None


def open_project(parent):
    """Get a valid project filename to open.

    Returns the path to an existing project file, or None if the user cancelled.
    *parent* is used as the window the dialog is associated with.
    """
    fd = wx.FileDialog(parent, message='Open project',
                       wildcard=FILE_WILDCARD,
                       style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_CHANGE_DIR)

    if fd.ShowModal() == wx.ID_OK:
        return fd.GetPath()
    else:
        return None


class ParameterSelectionCtrl(wx.ListCtrl, CheckListCtrlMixin):
    """Widget for selecting a subset of parameter values.

    Displays a list of parameter names and values with a checkbox next to each.
    *values* is a list of ``(key, value)`` pairs, where each ``key`` corresponds
    to a key in :data:`do3se.model.fields`.
    """
    def __init__(self, parent, values):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)

        self.values = values

        self.InsertColumn(0, 'Parameter')
        self.InsertColumn(1, 'Value')

        for k, v in self.values:
            index = self.InsertStringItem(sys.maxint, model.fields[k]['name'])
            self.SetStringItem(index, 1, str(v))

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def GetSelections(self):
        """Get currently selected parameter values as ``(key, value)`` pairs."""
        selections = list()
        for index in xrange(self.GetItemCount()):
            if self.IsChecked(index):
                selections.append(self.values[index])
        return selections


class PresetCreatorDialog(wx.Dialog):
    """Dialog for creating a named preset by selecting parameters."""
    def __init__(self, parent, values):
        wx.Dialog.__init__(self, parent, title='Save preset',
                           size=(500,300), style=wx.RESIZE_BORDER)
        self.SetSizer(wx.BoxSizer(wx.VERTICAL))

        s = wx.BoxSizer(wx.HORIZONTAL)
        s.Add(wx.StaticText(self, label="Preset name"), 0, wx.ALIGN_CENTER_VERTICAL)
        s.AddSpacer(5)
        self.name = wx.TextCtrl(self)
        s.Add(self.name, 1, wx.ALIGN_CENTER_VERTICAL)
        self.GetSizer().Add(s, 0, wx.EXPAND|wx.ALL, 5)

        self.selector = ParameterSelectionCtrl(self, values)
        self.GetSizer().Add(self.selector, 1, wx.EXPAND)

        buttons = self.CreateButtonSizer(wx.OK|wx.CANCEL)
        self.GetSizer().Add(buttons, 0, wx.ALL|wx.EXPAND, 5)

    def GetName(self):
        """Get supplied preset name."""
        return self.name.GetValue()

    def GetParameters(self):
        """Get selected parameters.
        
        See :meth:`ParameterSelectionCtrl.GetSelections`."""
        return self.selector.GetSelections()


def make_preset(parent, presets, values):
    """Create a new preset.

    Prompts the user for a preset name and which parameters to store, and if
    successful will add the preset to the *presets* dictionary.  The *values*
    supplied are ``(key, value)`` pairs where each ``key`` corresponds to a key
    in :data:`do3se.model.fields`.
    """
    pcd = PresetCreatorDialog(parent, values)
    
    # Bleh, have to resort to this ugly hack because the documented Validator
    # API in wxWidgets seems to be completely unimplemented in wxPython...
    while True:
        response = pcd.ShowModal()
        # If the user cancels, don't create a preset
        if response != wx.ID_OK:
            return None

        if len(pcd.GetParameters()) == 0:
            wx.MessageBox('No parameters selected',
                          'Save preset',
                          wx.OK|wx.ICON_ERROR,
                          parent)
            continue

        if len(pcd.GetName()) == 0:
            wx.MessageBox('Must supply a preset name',
                          'Save preset',
                          wx.OK|wx.ICON_ERROR,
                          parent)
            continue

        if pcd.GetName() in presets:
            response = wx.MessageBox('Overwrite preset "%s"?' % (pcd.GetName(),),
                                     'Save preset',
                                     wx.YES_NO|wx.ICON_QUESTION,
                                     parent)
            if response != wx.YES:
                continue

        # If we got this far, no problems!
        presets[pcd.GetName()] = pcd.GetParameters()
        break
