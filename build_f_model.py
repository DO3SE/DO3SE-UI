"""A setup.py for just building the fortran model to the _model module."""
import numpy
import os
import re
# Force use of gfortran
import sys
from numpy.distutils.core import setup, Extension, Distribution

sys.argv[1:] = ['config_fc', '--fcompiler=gnu95', '--f90flags="-fimplicit-none"', '--noopt'] + sys.argv[1:]
# sys.argv[1:] = ['config_fc', '--fcompiler=gnu95', '--f90flags="-fimplicit-none -Wall"', '--noopt'] + sys.argv[1:]


# Remove need for duplication - use file list from standalone model build
ext_files = [os.path.join('F', x) for x in
        re.findall(r'\w+\.f90',
            re.sub(r'(\w+)\.o', r'\1.f90',
                open(os.path.join('F', 'objects.mk'), 'r').read()))]
ext_name = '_model'


def buildpyf(filelist, target):
    from numpy.f2py import f2py2e
    f2py2e.callcrackfortran(filelist,
            {
                'signsfile': target + '.pyf',
                'module': target,
                'coutput': None,
                'f2py_wrapper_output': None,
                'debug': False,
                'verbose': False,
                'include_paths': list(),
                'do-lower': True
            }
    )
    return [target + '.pyf'] + filelist

if __name__ == "__main__":
    setup(
            name            = 'DO3SE',
            description     = 'DESCRIPT',
            version         = 'VERS',
            packages        = [],
            options         = {
                'py2exe': {
                    'includes': [
                        'dbhash',
                        ],
                    'excludes': [
                        # Ignore unused standard library packages to reduce size
                        '_ssl',
                        'doctest',
                        'pdb',
                        'difflib',
                        'inspect',
                        'tcl',
                        'Tkinter',
                        'bsddb',
                        'pydoc',
                        'compiler',
                        'distutils',
                        'email',
                        'numpy.core._dotblas',
                        # Packages that definitely cannot be removed
                        #'wx',
                        #'numpy',
                        #'unittest',
                        #'pyexpat',
                        ],
                    'dll_excludes': ['MSVCP90.dll'],
                    'bundle_files': 1,
                    'optimize': 2,
                },
            },
            ext_package     = 'do3se',
            ext_modules     = [
                Extension(ext_name, buildpyf(ext_files, ext_name))
            ],
    )