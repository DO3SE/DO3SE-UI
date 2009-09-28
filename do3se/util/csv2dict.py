"""
A very basic CSV to dictionary loader, designed for use with rows of numerical
values starting with a unique name for each row.

This code is Public Domain.
"""

def csv2dict(infile):
    """
    CSV to dict loader

    Takes an input file (in Comma Separated Values format) and builds a
    dictionary of rows from it, using the first row as the keys for row values,
    and the first column as the keys for rows.  Anything that can become a float
    will, everything else will be strings.
    """
    import csv
    
    data = dict()
    reader = csv.DictReader(infile)

    for row in reader:
        key = row.pop(reader.fieldnames[0])
        data[key] = dict((k, _attempt_float(v)) for k,v in row.iteritems() if v)

    return data


def _attempt_float(v):
    """
    Try to convert something to float, but leave it as a string if the
    conversion fails.
    """
    try:
        return float(v)
    except ValueError:
        return v
