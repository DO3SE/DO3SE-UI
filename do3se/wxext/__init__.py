""" 
Custom wxPython widgets
"""
import functools

import wx

from floatctrl import FloatCtrl
from listselectctrl import ListSelectCtrl
from presetchooser import PresetChooser
from staticbox2col import StaticBox2Col
from staticboxcanvas import StaticBoxCanvas
from pngpanel import PNGPanel

# Andrea Gavana's FloatSpin control
# (attempt to use built-in if wxPython is new enough)
try:
    from wx.lib.agw.floatspin import FloatSpin
except ImportError:
    from floatspin import FloatSpin

def autoeventskip(f):
    """Decorate class method to always ``evt.Skip()``.

    A convenience decorator to stop duplication of various forms of
    ``if evt: evt.Skip()`` and ``if evt is not None: evt.Skip()`` etc.  Used to
    decorate functions that always, unconditionally, pass the event on.
    """
    @functools.wraps(f)
    def new_f(self, evt):
        f(self, evt)
        if evt is not None:
            evt.Skip()
    return new_f


def static_bitmap_from_file(parent, filename):
    """Create a :class:`wx.StaticBitmap` from an image file."""
    bmp = wx.Image(filename).ConvertToBitmap()
    return wx.StaticBitmap(parent, wx.ID_ANY, bmp, size=(bmp.GetWidth(), bmp.GetHeight()))
