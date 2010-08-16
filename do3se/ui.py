import logging

import wx

from mainwindow2 import MainWindow


if __name__ == '__main__':
    logging.basicConfig(format="%(levelname)s -- %(name)s -- %(message)s",
                        level=logging.DEBUG)

    a = wx.App()
    w = MainWindow(None)
    w.SetSize((500,400))
    w.Show()
    a.MainLoop()
