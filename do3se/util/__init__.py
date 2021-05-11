"""
Generic utility functions.
"""
from __future__ import absolute_import

from builtins import zip
import csv
import itertools

from .ordereddict import OrderedDict

# try:
#     from collections import OrderedDict
# except ImportError:
#     from .ordereddict import OrderedDict


def setattrs(obj, d):
    """
    Using :obj:`d` as a mapping of attribute name to a new value, set the values
    of attributes on :obj:`obj`.
    """
    for k,v in d.items():
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
    data = dict()
    reader = csv.DictReader(infile)

    for row in reader:
        key = row.pop(reader.fieldnames[0])
        data[key] = dict((k, _attempt_float(v)) for k,v in row.items() if v)

    return data


def load_presets(infile):
    """Load presets from CSV file.

    The presets supplied with the application are defined in a CSV file where
    the first row is parameter IDs, the first column is preset names, and the
    rest of the values represent the value for each parameter for each preset.

    Empty parameters (empty strings) are ignored, to make it easier to define
    all presets in the same file while not supplying all parameters for each.

    The presets are returned as an :class:`OrderedDict` to preserve the order
    they are defined in, and each item in the dictionary is a list of
    ``(key, value)`` tuples.

    *infile* is a file-like object to read the CSV data from.
    """
    data = OrderedDict()
    reader = csv.reader(infile)

    # Read the first row as field names
    row_iter = iter(reader)
    fieldnames = next(row_iter)[1:]

    # Read the remaining rows, filtering out empty values and converting to
    # float where possible
    for row in row_iter:
        key = row.pop(0)
        data[key] = [(k, _attempt_float(v)) for k,v in zip(fieldnames, row) if v != '']

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
    return [dict(list(zip(keys, t))) for t in tuples]


def dicts_to_map(dicts, key, cls=dict):
    """Create a mapping of ``m[d[key]] = d`` for a list of dicts."""
    return cls((d[key], d) for d in dicts)
