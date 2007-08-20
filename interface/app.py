#!/usr/bin/python

from tools import _verbose

import do3se_xrc as ui

import os
import wx

#import w_main

class DOSEApp(wx.App):
    def OnInit(self):
        #self.window = w_main.Main(None)
        self.window = ui.xrcwindow_main(None)
        self.window.Show()
        return True

if __name__ == '__main__':
    app = DOSEApp(False)
    #print wx.FileSelector("Open a file")
    app.MainLoop()
