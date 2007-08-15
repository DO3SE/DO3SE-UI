#!/usr/bin/python

import wx
from wx import xrc

class DOSEApp(wx.App):
    def OnInit(self):
        return True

if __name__ == '__main__':
    app = DOSEApp(False)
    print wx.FileSelector("Open a file")
    app.MainLoop()
