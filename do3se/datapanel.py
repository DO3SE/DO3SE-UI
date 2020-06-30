import wx
import wx.grid

import model


class DataTable(wx.grid.PyGridTableBase):
    """Virtual data table for model results.

    Implements virtual table interface to lookup cell values in *data*.
    """
    #: Available column field keys, in the order they are defined in
    #: :mod:`~do3se.model`, to display values in the correct columns
    COLUMNS = list(model.output_fields.keys())
    #: Column labels in the same order as :data:`COLUMNS`
    COLUMN_LABELS = [x['short'] for x in model.output_fields.values()]

    def __init__(self, data):
        wx.grid.PyGridTableBase.__init__(self)
        self.data = data

    def GetNumberRows(self):
        """Get the number of rows in the table."""
        return len(self.data)

    def GetNumberCols(self):
        """Get the number of columns in the table."""
        return len(self.COLUMNS)

    def IsEmptyCell(self, row, col):
        """Check if the cell at (*row*, *col*) is empty.

        Always returns false, since there shouldn't be any empty cells and it's
        cheaper than actually checking.
        """
        return False

    def GetValue(self, row, col):
        """Get the value of the cell at (*row*, *col*)."""

        return str(self.data[row][self.COLUMNS[col]])

    def SetValue(self, row, col, value):
        """Set the value of the cell at (*row*, *col*).

        Does nothing, since the results are not editable.
        """
        pass

    def GetColLabelValue(self, col):
        """Get the label for column with index *col*."""
        return self.COLUMN_LABELS[col]


class DataGrid(wx.grid.Grid):
    """Model results data grid.

    Attempting to show all of the results in a conventional table is too CPU-
    and RAM-intensive, since an average data run will have in excess of 500,000
    cells.  Instead a virtual table (:class:`DataTable`) is used to provide
    on-demand access to cell contents.
    """
    def __init__(self, parent, data):
        wx.grid.Grid.__init__(self, parent, -1)

        self.EnableEditing(False)
        self.SetColLabelAlignment(wx.ALIGN_LEFT, wx.ALIGN_BOTTOM)

        self.SetTable(DataTable(data), True)


class DataPanel(wx.Panel):
    """A panel containing nothing but a :class:`DataGrid`.

    Create a panel containing a :class:`DataGrid` for displaying *data*.
    """
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent)

        s = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(s)

        grid = DataGrid(self, data)
        s.Add(grid, 1, wx.EXPAND|wx.ALL, 5)
