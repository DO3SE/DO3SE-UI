import io

import wx

from _resources import *


def get_memoryfs_stream(filename):
    """Get a MemoryFS file as a :class:`StringIO` object."""
    f = wx.FileSystem().OpenFile('memory:' + filename)
    data = io.StringIO(f.Stream.read().decode('utf-8'))
    return data
