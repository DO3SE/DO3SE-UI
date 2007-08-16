#!/usr/bin/python

import wx
from wx import xrc

import window_main

class DOSEApp(wx.App):
    def OnInit(self):
        self.window = window_main.Main(None)
        self.window.Show()
        return True

if __name__ == '__main__':
    app = DOSEApp(False)
    #print wx.FileSelector("Open a file")
    app.MainLoop()
