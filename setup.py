#!/usr/bin/env python

import os
import re
from glob import glob

import numpy
from numpy.distutils.core import setup, Extension, Distribution

import do3se.application

try:
    import py2exe
except ImportError:
    pass

application = do3se.application.app_name
description = do3se.application.app_description
version     = do3se.application.app_version

manifest = '''
<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
  <assemblyIdentity
    version="0.6.8.0"
    processorArchitecture="x86"
    name="%(app)s"
    type="win32"
  />
  <description>%(description)s</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="asInvoker"
          uiAccess="false"
        />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.VC90.CRT"
        version="9.0.21022.8"
        processorArchitecture="x86"
        publicKeyToken="1fc8b3b9a1e18e3b"
      />
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="x86"
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
                'debug': False,
                'verbose': False,
                'include_paths': list(),
                'do-lower': True
            }
    )
    return [target + '.pyf'] + filelist

if __name__ == "__main__":

    # NumPy is stupid, so we have to hack the stuff in here instead
    Distribution.zipfile = None
    Distribution.com_server = []
    Distribution.ctypes_com_server = []
    Distribution.service = []
    Distribution.console = []
    Distribution.isapi = []
    Distribution.windows = [{
            'script': "run-newui.py",
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
                ('resources', [
                    'resources/default_veg_presets.csv',
                    'resources/resistance.png',
                    'resources/transfer.png',
                    'resources/functions.png',
                    ]
                ),
                ('Microsoft.VC90.CRT',
                    glob('resources/Microsoft.VC90.CRT/*')),
                ],
            options         = {
                'build': build_opts,
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
