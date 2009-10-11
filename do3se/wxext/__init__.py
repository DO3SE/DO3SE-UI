# 
# Custom wxPython widgets
#

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
