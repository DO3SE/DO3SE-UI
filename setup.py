#!/usr/bin/env python

import do3se.application

application = do3se.application.app_name
description = do3se.application.app_description
version     = do3se.application.app_version

from numpy.distutils.core import setup, Extension, Distribution
import os

try:
    import py2exe
except ImportError:
    pass

# NumPy doesn't play nice with py2exe, an __init__.py is missing - let's fix it!
import numpy
path = os.path.join(os.path.dirname(numpy.__file__),
                    'distutils', 'tests', '__init__.py')
open(path, 'a').close()

# Find the DLLs we need from wxPython (for Python 2.5, anyway...)
import wx, glob
wxpath = os.path.dirname(wx.__file__)
wxdlls = glob.glob(os.path.join(wxpath, 'msvcp??.dll'))
wxdlls.append(os.path.join(wxpath, 'gdiplus.dll'))

manifest = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(app)s"
    type="win32"
/>
<description>%(description)s</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
''' % dict(app=application, description=description)

build_opts = dict()
if os.name == 'nt':
    build_opts['compiler'] = 'mingw32'

files = [os.path.join('F', x) for x in [
                        'constants.f90',
                        'params_veg.f90',
                        'params_site.f90',
                        'inputs.f90',
                        'variables.f90',
                        'functions.f90',
                        'environmental.f90',
                        'evapotranspiration.f90',
                        'irradiance.f90',
                        'phenology.f90',
                        'r.f90',
                        'soil.f90',
                        'o3.f90',
                        'run.f90',
]]

def buildpyf(filelist, target):
    from numpy.f2py import f2py2e
    f2py2e.callcrackfortran(filelist,
            {
                'signsfile': target,
                'module': 'do3se_fortran',
                'debug': False,
                'verbose': False,
                'include_paths': list(),
                'do-lower': True
            }
    )
    return [target] + filelist

if __name__ == "__main__":

    # NumPy is stupid, so we have to hack the stuff in here instead
    Distribution.zipfile = None
    Distribution.com_server = []
    Distribution.ctypes_com_server = []
    Distribution.service = []
    Distribution.console = []
    Distribution.isapi = []
    Distribution.windows = [{
            'script': "run-do3se.py",
            'other_resources': [(24, 1, manifest)],
    }]

    setup(
            name            = application,
            description     = description,
            version         = version,
            author          = 'Alan Briolat',
            author_email    = 'sei@alanbriolat.co.uk',
            packages        = ['do3se', 'do3se.util', 'do3se.wxext'],
            data_files      = [
                ('.', wxdlls),
                ('resources', [
                    'resources/default_veg_presets.csv',
                    'resources/resistance.png',
                    ]
                ),
            ],
            options         = {
                'build': build_opts,
                'py2exe': {
                    'includes': [
                        'dbhash',
                        'simplejson',
                        ],
                    'packages': [
                        'numpy',
                        ],
                    'bundle_files': 1,
                    'optimize': 2,
                },
            },
            ext_package     = 'do3se',
            ext_modules     = [
                Extension('do3se_fortran', buildpyf(files, 'do3se_fortran.pyf'))
            ],
    )
