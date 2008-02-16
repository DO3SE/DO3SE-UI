#!/usr/bin/env python


from numpy.distutils.core import setup, Extension
import os

try:
    import py2exe
except ImportError:
    pass

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
                'module': 'dose_f',
                'debug': False,
                'verbose': False,
                'include_paths': list(),
                'do-lower': True
            }
    )
    return [target] + filelist

if __name__ == "__main__":
    setup(
            name            = 'DOSE-UI',
            description     = 'DOSE Model User Interface',
            version         = '0.1',
            author          = 'Alan Briolat',
            author_email    = 'ab544@cs.york.ac.uk',
            packages        = ['ui', 'ui.panels'],
            options         = {
                'build': build_opts,
                'py2exe': {'includes': ['dbhash', 'numpy']},
            },
            ext_package     = 'ui',
            ext_modules     = [
                Extension('dose_f', buildpyf(files, 'dose_f.pyf'))
            ],
            windows=["dose-ui"],
    )
