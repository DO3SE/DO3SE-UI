#!/usr/bin/python

# Import wxWidgets library
import wx
from wx import xrc

class ColWin(wx.Window):
    def __init__(self, parent, BackColour):
        wx.Window.__init__(self, parent)
        self.SetBackgroundColour(BackColour)

class InputPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.FlexGridSizer(cols = 2, vgap = 5, hgap = 5)
        sizer.SetFlexibleDirection(wx.HORIZONTAL)
        sizer.AddGrowableCol(1, 1)
        
        sizer.Add(wx.StaticText(self, label = "Input file:"), flag = wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_LEFT)
        fpc = wx.FilePickerCtrl(self)
        sizer.Add(fpc, flag = wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)

        self.SetSizer(sizer)


class MainPanel(wx.Panel):
    def __init__(self, parent):
        # Pass parameters to wxFrame constructor
        wx.Panel.__init__(self, parent)


        wgreen = ColWin(self, wx.GREEN)
        wred = ColWin(self, wx.RED)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(wgreen, 1, wx.EXPAND)
        vsizer.Add(wred, 1, wx.EXPAND)
        
        self.SetSizer(vsizer)

class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        notebook = wx.Notebook(self)
        sizer.Add(notebook, 1, wx.EXPAND)
        input = InputPanel(notebook)
        notebook.AddPage(input, "Input settings")

        

class Application(wx.App):
    def OnInit(self):
        #self.window = winMain(None, title = "This is a test")
        #self.window = xrc_res.LoadFrame(None, 'MainWindow')
        self.window = MainWindow(None)

        self.window.Show()
        return True

if __name__ == "__main__":
    app = Application(False)
    app.MainLoop()


