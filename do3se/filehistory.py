import wx

class FileHistory(wx.FileHistory):
    """
    Recent file history

    A wrapper around wxFileHistory which uses the application config to load the
    initial set of recent files, and keeps the config up to date every time a 
    recent file is added.
    """
    def __init__(self, parent):
        """
        Constructor

        Create the wxFileHistory in the way we want and load from the config.
        """
        self.parent = parent

        wx.FileHistory.__init__(self, 9, wx.ID_FILE1)
        # Initialise with existing paths
        for p in self.parent.app.config['file_history']:
            wx.FileHistory.AddFileToHistory(self, p)


    def AddFileToHistory(self, path):
        """
        Add file to history

        Add a file to the recent files list in the normal way, but also add it 
        to the config.
        """
        wx.FileHistory.AddFileToHistory(self, path)
        # Save to configuration file
        self.parent.app.config.add_to_file_history(path)
