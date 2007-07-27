#!/usr/bin/python

import wx
from wx import xrc

class MyApp(wx.App):
    def OnInit(self):
        self.res = xrc.XmlResource('DO3SE.xrc')
        self.init_frame()
        return True

    def init_frame(self):
        self.frame = self.res.LoadDialog(None, 'DIALOG2')
        self.frame.Show()

if __name__ == '__main__':
    app = MyApp(False)
    app.MainLoop()
