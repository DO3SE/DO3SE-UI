import wx

from tools import _verbose

class Main(wx.Frame):
    # Title base string - titles are this or "title_base - title"
    title_base = "Deposition of Ozone and Stomatal Exchange"

    def __init__(self, parent):
        _verbose("Initializing main window")

        wx.Frame.__init__(self, parent, title = self.title_base)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer1)

        self.placeholder = Main_Placeholder(self)

        sizer1.Add(self.placeholder, proportion = 1, flag = wx.EXPAND)

        self.init_menu()

    def init_menu(self):
        _verbose("Initializing main menu")

        self.ID_FILE_OPEN = wx.NewId()
        self.ID_FILE_CLOSE = wx.NewId()
        self.ID_FILE_QUIT = wx.NewId()

        # Create menubar
        menubar = wx.MenuBar()

        # Create 'File' menu
        file_menu = wx.Menu()
        file_menu.Append(self.ID_FILE_OPEN, '&Open...')
        file_menu.Append(self.ID_FILE_CLOSE, '&Close')
        file_menu.AppendSeparator()
        file_menu.Append(self.ID_FILE_QUIT, '&Quit')
        
        # Menu item bindings
        self.Bind(wx.EVT_MENU, self.FileOpen, id = self.ID_FILE_OPEN)
        self.Bind(wx.EVT_MENU, self.FileClose, id = self.ID_FILE_CLOSE)
        self.Bind(wx.EVT_MENU, self.FileQuit, id = self.ID_FILE_QUIT)


        # Add the 'File' menu
        menubar.Append(file_menu, '&File')
        # Display the menubar
        self.SetMenuBar(menubar)

    def SetTitle(self, title):
        """Override the SetTitle() method to append the supplied title to 
        the title_base value.  If title = None, then just title_base is 
        displayed
        """
        if title:
            wx.TopLevelWindow.SetTitle(self, "%s - %s" % (self.title_base, title))
        else:
            wx.TopLevelWindow.SetTitle(self, self.title_base)

    def FileOpen(self, event):
        path = wx.FileSelector("Open CSV data file", wildcard = "Comma-Separated Values (*.csv)|*.csv|All files (*.*)|*.*")
        if path:
            pass
        else:
            msg = wx.MessageDialog(self, "No file selected", self.title_base, wx.OK | wx.ICON_ERROR | wx.STAY_ON_TOP)
            msg.ShowModal()

    def FileClose(self, event):
        pass

    def FileQuit(self, event):
        self.Close()


class Main_Placeholder(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)
        self.label = wx.StaticText(self, style = wx.ALIGN_CENTER, \
                label = "To start, open a file using the 'File -> Open...' menu.")
        sizer.Add(self.label, proportion = 1, flag = wx.ALIGN_CENTRE_VERTICAL)
        self.label.SetBackgroundColour(wx.GREEN)
