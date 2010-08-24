import os.path

import wx


#: Default/suggested file extension for project files
FILE_EXTENSION = '.do3se'
#: Wildcard string for :class:`wx.FileDialog`
FILE_WILDCARD = 'DO3SE project files (*%s)|*%s|All (*.*)|*.*' % (FILE_EXTENSION, FILE_EXTENSION)


def save_project(parent, default='project'+FILE_EXTENSION):
    """
    Get a valid project filename for saving a project.

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
    """
    Get a valid project filename to open.

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
