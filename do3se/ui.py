import wx

import ui_xrc


class MainWindow(ui_xrc.xrcframe_mainwindow):
    pass


class ProjectWindow(ui_xrc.xrcframe_projectwindow):

    def OnButton_btn_errors(self, evt):
        self.pnl_errors.Show(not self.pnl_errors.IsShown())
        self.pnl_errors.GetContainingSizer().Layout()

if __name__ == '__main__':
    import glob
    import os.path

    a = wx.App()
    w = MainWindow(None)
    w.SetSize((500,400))
    w.list_recent.AppendItems(map(os.path.abspath, glob.glob("do3se/*.py")))
    w.Show()
    pw = ProjectWindow(None)
    pw.SetSize((600,400))
    pw.Show()
    a.MainLoop()
