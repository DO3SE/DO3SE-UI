"""
Generic utility functions.
"""

def setattrs(obj, d):
    """
    Using :obj:`d` as a mapping of attribute name to a new value, set the values
    of attributes on :obj:`obj`.
    """
    for k,v in d.iteritems():
        setattr(obj, k, v)


def csv2dict(infile):
    """
    CSV data loader.

    The following CSV data format is assumed:

      * The first row contains field names (excluding the first column),
      * The first column contains "row names" (excluding the first row),
      * All other cells represent the row's value for the column's field.
    
    From a file-like object :obj:`infile`, a dictionary is created which maps
    from a row name to another dictionary, which in turn maps from field names
    to values.

    Any value that can become a float will become a float, everything else
    remains as strings.
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


def to_dicts(keys, tuples):
    """Given an n-tuple of keys and a list of n-tuples, make a list of dicts."""
    return [dict(zip(keys, t)) for t in tuples]


def dicts_to_map(dicts, key, cls=dict):
    """Create a mapping of ``m[d[key]] = d`` for a list of dicts."""
    return cls((d[key], d) for d in dicts)
