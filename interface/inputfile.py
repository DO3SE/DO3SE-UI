import csv, copy, exceptions

class InputFileError(exceptions.Exception):
    pass

class InputFile:
    def __init__(self, path):
        """Only store the path to the file here.
        """
        self.path = path
        self.fields = None
        self.data = None
        
    def __iter__(self):
        """Allow 'for row in myinputfile:' constructs.
        """
        if not self.data:
            raise InputFileError("Data not yet loaded")
        else:
            return iter(self.data)

    def SetFields(self, fields):
        """Set the field order for the CSV.
        """
        self.fields = fields

    def GetFields(self):
        """Retrieve the CSV field order.
        """
        return self.fields

    def Load(self):
        """Load the data from the CSV file.
        """

        if not self.fields:
            raise InputFileError("Field order not yet set")

        file = open(file)

        self.linecount = 0
        self.data = []
        
        r = csv.DictReader(file, fieldnames = fields)

        for l in r:
            self.linecount = self.linecount + 1
            self.data.append({'lineno': self.linecount, 'data': copy.deepcopy(l)})

        close(file)

if __name__ == "__main__":
    f = InputFile('../2003_input.csv', ['mm', 'mdd', 'dd', 'hr', 'ts_c', 'vpd', 'precip', 'uh', 'o3_ppb_zr', 'idrctt', 'idfuse', 'zen'])

    for i in f:
        print i['lineno']
