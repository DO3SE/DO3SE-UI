import logging

import wx

import ui_xrc
from projectwindow import ProjectWindow


class MainWindow(ui_xrc.xrcframe_mainwindow):
    def OnListbox_list_recent(self, evt):
        enabled = self.list_recent.GetSelection() != wx.NOT_FOUND
        self.btn_open_selected.Enable(enabled)

    def OnListbox_dclick_list_recent(self, evt):
        self.OnButton_btn_open_selected(evt)

    def OnButton_btn_new(self, evt):
        if open_project():
            self.Close()

    def OnButton_btn_open_selected(self, evt):
        projectfile = self.list_recent.GetString(self.list_recent.GetSelection())
        if open_project(projectfile):
            self.Close()


def open_project(projectfile=None):
    """
    Open a project window, either for an existing project file or for a new
    project.  Returns False if no window was created, otherwise returns True.
    """
    w = ProjectWindow(projectfile)
    w.Show()
    return True
