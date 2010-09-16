import os.path
import sys

import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin

import model
import ui_xrc
import wxext


#: Default/suggested file extension for project files
PROJECT_EXTENSION = '.do3se'
#: Wildcard string for :class:`wx.FileDialog`
PROJECT_WILDCARD = 'DO3SE project files (*%s)|*%s|All (*.*)|*.*' % (PROJECT_EXTENSION, PROJECT_EXTENSION)
#: Default/suggested file extension for data files
DATAFILE_EXTENSION = '.csv'
DATAFILE_WILDCARD = 'Comma-separated values (*%s)|*%s|All (*.*)|*.*' % (DATAFILE_EXTENSION, DATAFILE_EXTENSION)


def save_project(parent, default='project'+PROJECT_EXTENSION):
    """Get a valid project filename for saving a project.

    Returns either a valid file path to save the project as, or None if the user
    cancelled.  *parent* is used as the window the dialog is associated with,
    and *default* is a default file path to use.
    """
    fd = wx.FileDialog(parent, message='Save project',
                       defaultDir=os.path.dirname(default),
                       defaultFile=os.path.basename(default),
                       wildcard=PROJECT_WILDCARD,
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
                       wildcard=PROJECT_WILDCARD,
                       style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_CHANGE_DIR)

    if fd.ShowModal() == wx.ID_OK:
        return fd.GetPath()
    else:
        return None


def save_datafile(parent, default='output'+DATAFILE_EXTENSION):
    """Promet the user for an output file name.

    Returns the path to save the output file as, unless the user cancelled, in
    which case None is returned.
    """
    fd = wx.FileDialog(parent, message='Save project',
                       defaultDir=os.path.dirname(default),
                       defaultFile=os.path.basename(default),
                       wildcard=DATAFILE_WILDCARD,
                       style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT|wx.FD_CHANGE_DIR)

    if fd.ShowModal() == wx.ID_OK:
        return fd.GetPath()
    else:
        return None


def open_datafile(parent):
    """Prompt the user to select a data file to open.
    
    Returns the path to the selected file, or None if the user cancelled.
    """
    fd = wx.FileDialog(parent, message='Open data file',
                       wildcard=DATAFILE_WILDCARD,
                       style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_CHANGE_DIR)
    if fd.ShowModal() == wx.ID_OK:
        return fd.GetPath()
    else:
        return None


class ParameterSelectionCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    """Widget for selecting a subset of parameter values.

    Displays a list of parameter names and values with a checkbox next to each.
    """
    def __init__(self, parent, values=[]):
        wx.ListCtrl.__init__(self, parent, style=wx.LC_REPORT)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, 'Parameter')
        self.InsertColumn(1, 'Value')

        self.SetValues(values)

    def SetValues(self, values):
        """Set the available values to select from.

        *values* is a list of ``(key, value)`` pairs, where each ``key`` corresponds
        to a key in :data:`do3se.model.paramdefs`.
        """
        self.values = values

        self.DeleteAllItems()

        for k, v in self.values:
            index = self.InsertStringItem(sys.maxint, model.paramdefs[k]['name'])
            self.SetStringItem(index, 1, str(v))

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def GetSelections(self):
        """Get currently checked parameter values as ``(key, value)`` pairs."""
        selections = list()
        for index in xrange(self.GetItemCount()):
            if self.IsChecked(index):
                selections.append(self.values[index])
        return selections

    def CheckAll(self):
        """Check all items."""
        for index in xrange(self.GetItemCount()):
            self.CheckItem(index, True)


class PresetCreatorDialog(wx.Dialog):
    """Dialog for creating a named preset by selecting parameters."""
    def __init__(self, parent, values):
        wx.Dialog.__init__(self, parent, title='Save preset', size=(500,300),
                           style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)
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
    in :data:`do3se.model.paramdefs`.
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


class PresetManagerDialog(ui_xrc.xrcdialog_presets):
    """Dialog for applying or deleting presets."""
    def __init__(self, parent, user_presets, default_presets):
        ui_xrc.xrcdialog_presets.__init__(self, parent)

        self.user_presets = user_presets
        self.default_presets = default_presets

        self.SetSize((700, 500))
        self.SetAffirmativeId(wx.ID_APPLY)

        # Replace the placeholder panel with a ParameterSelectionCtrl
        self.paramlist = ParameterSelectionCtrl(self)
        self.paramlist_dummy.GetContainingSizer().Replace(self.paramlist_dummy, self.paramlist)
        self.paramlist_dummy.Destroy()
        self.paramlist.GetContainingSizer().Layout()

        # Initialise presets list
        plroot = self.presetlist.AddRoot('')
        # (user-defined presets)
        self.user_presets_root = self.presetlist.AppendItem(plroot, 'User presets')
        for k in self.user_presets.iterkeys():
            self.presetlist.AppendItem(self.user_presets_root, k)
        self.presetlist.Expand(self.user_presets_root)
        # (application-default presets)
        self.default_presets_root = self.presetlist.AppendItem(plroot, 'Default presets')
        for k in self.default_presets.iterkeys():
            self.presetlist.AppendItem(self.default_presets_root, k)
        self.presetlist.Expand(self.default_presets_root)

        self.presetlist.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged_presetlist)

    def GetParameters(self):
        """Get the selected parameters to apply."""
        return self.paramlist.GetSelections()

    @wxext.autoeventskip
    def OnTreeSelChanged_presetlist(self, evt):
        """When a preset is selected, update the parameters list."""
        item = evt.GetItem()
        label = self.presetlist.GetItemText(item)
        parent = self.presetlist.GetItemParent(item)

        # Selected a user-defined preset
        if parent == self.user_presets_root:
            self.paramlist.SetValues(self.user_presets[label])
            self.paramlist.CheckAll()

        # Selected a default preset
        elif parent == self.default_presets_root:
            self.paramlist.SetValues(self.default_presets[label])
            self.paramlist.CheckAll()

        # Enabled delete button only if user preset selected
        self.wxID_DELETE.Enable(parent == self.user_presets_root)

    @wxext.autoeventskip
    def OnButton_wxID_DELETE(self, evt):
        """Delete the selected user-created preset."""
        item = self.presetlist.GetSelection()
        parent = self.presetlist.GetItemParent(self.presetlist.GetSelection())
        if parent == self.user_presets_root:
            label = self.presetlist.GetItemText(item)
            response = wx.MessageBox('Delete preset "%s"?  This cannot be undone.' % (label,),
                                     'Delete preset', wx.YES_NO|wx.ICON_QUESTION, self)
            if response == wx.YES:
                del self.user_presets[label]
                self.presetlist.Delete(item)
                self.paramlist.SetValues([])


def apply_preset(parent, user_presets, default_presets):
    pmd = PresetManagerDialog(parent, user_presets, default_presets)

    response = pmd.ShowModal()
    if response == wx.ID_APPLY:
        return pmd.GetParameters()
    else:
        return []
