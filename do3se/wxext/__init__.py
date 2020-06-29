"""
Custom wxPython widgets
"""
from __future__ import absolute_import
import functools

import wx

from .listselectctrl import ListSelectCtrl, SaveListSelectCtrl
from .presetchooser import PresetChooser

# Andrea Gavana's FloatSpin control
# (attempt to use built-in if wxPython is new enough)
try:
    from wx.lib.agw.floatspin import FloatSpin
except ImportError:
    from .floatspin import FloatSpin

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


class AutowrapStaticText(wx.StaticText):
    """:class:`wx.StaticText` which automatically wraps it's text.

    Text in :class:`wx.StaticText` doesn't automatically wrap on wxMSW, so this
    class catches resize events and wraps the text accordingly.
    """
    def __init__(self, parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name=wx.StaticTextNameStr, bg=None):
        self._label = label
        wx.StaticText.__init__(self, parent, id, label, pos, size, style, name)
        self.SetBackgroundColour(bg)
        self.Bind(wx.EVT_SIZE, self.OnResize)

    def SetLabel(self, label):
        """Cache the unmangled text when setting the label."""
        self._label = label
        wx.StaticText.SetLabel(self, label)

    def GetRawLabel(self):
        """Get the unmangled label (the :meth:`Wrap` method inserts newlines)."""
        return self._label

    def OnResize(self, evt):
        """Re-wrap the label text on resize."""
        pass
        # TODO: Below causes recursion error
        # wx.StaticText.SetLabel(self, self._label)
        # self.Wrap(evt.GetSize().x)
        # evt.Skip()
