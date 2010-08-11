import logging

import wx

import ui_xrc
from fields import *


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


class ProjectWindow(ui_xrc.xrcframe_projectwindow):
    log = logging.getLogger('do3se.ui.projectwindow')

    def __init__(self, projectfile):
        ui_xrc.xrcframe_projectwindow.__init__(self, None)
        self.SetSize((500,400))
        
        if projectfile:
            self.log.info("Opening project " + projectfile)
        else:
            self.log.info("Creating new project")


        root = Fields()

        fg1 = FieldGroup(root)
        fg1.append(Field(root, "Foo"))
        fg1.append(Field(root, "Bar"))
        fg1.append(Field(root, "Baz"))
        fg1.append(Field(root, "Bozzle"))
        root.add_group(fg1, "Foo bar baz bozzle")

        fg2 = FieldGroup(root)
        fg2.append(Field(root, "What the hell?"))
        root.add_group(fg2, "Om nom nom")

        root.add_to_ui(self.tb_main)

    def OnClose(self, evt):
        evt.Skip()

    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()

    def OnButton_btn_close(self, evt):
        self.Close()


def open_project(projectfile=None):
    """
    Open a project window, either for an existing project file or for a new
    project.  Returns False if no window was created, otherwise returns True.
    """
    w = ProjectWindow(projectfile)
    w.Show()
    return True


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s -- %(name)s -- %(message)s",
                        level=logging.DEBUG)

    a = wx.App()
    w = MainWindow(None)
    w.SetSize((500,400))
    w.Show()
    a.MainLoop()
