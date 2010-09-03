import wx
import wx.grid as gridlib

import model


class DataTable(gridlib.PyGridTableBase):

    def __init__(self, dataset):
        gridlib.PyGridTableBase.__init__(self)

        self.dataset = dataset
        self.fields = model.output_fields.keys()
        self.col_labels = [x['short'] for x in model.output_fields.itervalues()]


    def GetNumberRows(self):
        return len(self.dataset.results)


    def GetNumberCols(self):
        return len(self.fields)


    def IsEmptyCell(self, row, col):
        return False


    def GetValue(self, row, col):
        return str(self.dataset.results[row][self.fields[col]])


    def SetValue(self, row, col, value):
        pass


    def GetColLabelValue(self, col):
        return self.col_labels[col]


class DataGrid(gridlib.Grid):

    def __init__(self, parent, dataset):
        gridlib.Grid.__init__(self, parent, -1)

        self.EnableEditing(False)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)

        table = DataTable(dataset)

        self.SetTable(table, True)



class DataPanel(wx.Panel):
    def __init__(self, parent, dataset):
        wx.Panel.__init__(self, parent)

        self.dataset = dataset

        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        grid = DataGrid(self, dataset)
        s.Add(grid, 1, wx.EXPAND|wx.ALL, 6)
