import wx

import ui_xrc


class MainWindow(ui_xrc.xrcframe_mainwindow):

    def OnListbox_list_recent(self, evt):
        enabled = self.list_recent.GetSelection() != wx.NOT_FOUND
        self.btn_open_selected.Enable(enabled)

    def OnListbox_dclick_list_recent(self, evt):
        self.OnButton_btn_open_selected(evt)


class ProjectWindow(ui_xrc.xrcframe_projectwindow):

    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()


if __name__ == '__main__':
    a = wx.App()
    w = MainWindow(None)
    w.SetSize((500,400))
    w.Show()
    pw = ProjectWindow(None)
    pw.SetSize((600,400))
    pw.Show()
    a.MainLoop()
