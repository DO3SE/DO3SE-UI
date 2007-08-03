#!/usr/bin/python

import wx
from wx import xrc

class MyApp(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource('DO3SE.xrc')
        self.init_frame()
        return True

    def init_frame(self):
        self.frame = self.res.LoadDialog(None, 'FileChooser')
        self.dirlist = xrc.XRCCTRL(self.frame, 'FileChooser_DirList')
        self.frame.Bind(wx.EVT_CLOSE, self.OnQuit, id=xrc.XRCID('FileChooser'))
        self.frame.Show()

    def OnQuit(self, event):
        path = self.dirlist.GetFilePath()
        if path:
            print path
        else:
            print "No path selected"
        self.Exit()

if __name__ == '__main__':
    app = MyApp(False)
    print wx.FileSelector("Open a file")
    app.MainLoop()
