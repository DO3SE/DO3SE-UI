import wx
import wx.grid as gridlib

from .. import wxext
from .. import dose
from ..app import logging, app

class Data(wx.Panel):
    def __init__(self, parent, dataset):
        wx.Panel.__init__(self, parent)

        self.dataset = dataset

        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        grid = gridlib.Grid(self)
        s.Add(grid, 1, wx.EXPAND|wx.ALL, 6)

        grid.CreateGrid(len(self.dataset.results), len(dose.output_fields))
        grid.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)
        #grid.SetDefaultRenderer(gridlib.GridCellNumberRenderer())
        grid.EnableEditing(False)

        colmap = dict()
        i = 0
        for x in dose.output_fields:
            colmap[x['variable']] = i
            grid.SetColLabelValue(i, x['short'])
            i += 1

        i = 0
        for row in self.dataset.results:
            for k, c in colmap.iteritems():
                grid.SetCellValue(i, c, str(row[k]))
            i += 1
