import StringIO

import wx

from _resources import *


def get_memoryfs_stream(filename):
    """Get a MemoryFS file as a :class:`StringIO` object."""
    f = wx.FileSystem().OpenFile('memory:' + filename)
    data = StringIO.StringIO(f.Stream.read())
    return data
