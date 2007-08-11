#!/usr/bin/python

import types, csv, copy

class InputFile:
    def __init__(self, file, fields):
        file = open(file)

        self.linecount = 0
        self.data = []
        
        r = csv.DictReader(file, fieldnames = fields)

        for l in r:
            self.linecount = self.linecount + 1
            self.data.append({'lineno': self.linecount, 'data': copy.deepcopy(l)})

        close(file)
        
    def __iter__(self):
        return iter(self.data)

if __name__ == "__main__":
    f = InputFile('../2003_input.csv', ['mm', 'mdd', 'dd', 'hr', 'ts_c', 'vpd', 'precip', 'uh', 'o3_ppb_zr', 'idrctt', 'idfuse', 'zen'])

    for i in f:
        print i['lineno']
