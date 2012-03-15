def namelist_generator(var, name=''):
    """Generate namelist lines for a variable.

    Produces a Fortran namelist line for each value in *var*, using *name* as
    the parent variable name.  For a simple value this is ``name = var``.  For
    more complex cases (lists, tuples and dicts) the function recurses, adding
    ``%key`` or ``(index)`` to the variable name as appropriate.

    As long as all non-sequence, non-mapping values have a ``repr()`` that
    Fortran will understand and all variable names (dictionary keys) are valid
    Fortran identifiers, the resulting lines should be understood by a Fortran
    namelist read.
    """
    # Dicts: use the var%component syntax (except in the top-level case)
    if isinstance(var, dict):
        for key, value in var.iteritems():
            newname = key if name == '' else name + '%' + key
            for line in namelist_generator(value, newname):
                yield line
    # Lists: generate array assignments, starting at 1 to match Fortran
    elif isinstance(var, list) or isinstance(var, tuple):
        for i, value in enumerate(var, 1):
            for line in namelist_generator(value, '{0}({1})'.format(name, i)):
                yield line
    # Everything else: Python's repr() of the value should be sufficient,
    # since Fortran's namelist support is fairly permissive
    else:
        yield name + ' = ' + repr(var)


def generate_namelist(namelist, data):
    """Create a namelist from a dictionary.
    
    Creates text that can be read by Fortran using ``read (..., nml=namelist)``
    to set the values of variables present in *data*.  Nesting of compound
    types (using dicts) and arrays (using lists or tuples) is allowed.  *data*
    should obviously match what the corresponding namelist in the target
    Fortran program allows.
    """
    return '&{0}\n{1}\n/\n'.format(namelist, '\n'.join(namelist_generator(data)))
