"""This is a WIP updated setup file.

TODO:
- Bring in manifest
- Build fortran
- Implement py2exe

"""
import setuptools
# from setuptools import setup
from glob import glob
import os
import re
from numpy.distutils.core import Extension, setup
from do3se.version import app_version, app_name
with open("README.md", "r") as fh:
    long_description = fh.read()

ext_files = [os.path.join('F', x) for x in
             re.findall(r'\w+\.f90',
                        re.sub(r'(\w+)\.o', r'\1.f90',
                               open(os.path.join('F', 'objects.mk'), 'r').read()))]

all_ext_files = ['do3se/_model.pyf'] + ext_files

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

setup(
    name=app_name,
    version=app_version,
    author='Sam Bland | Alan Briolat',
    author_email='sam.bland@sei.org',
    description="DO3SE model python API",
    setup_requires=['numpy'],
    install_requires=[
        'numpy',
        'future',
        'pandas',
        ''
    ],
    extras_require={
        'cli': ['pytest', 'numpy', 'pandas', 'click'],
        'grid': ['xarray', 'netCDF4', 'pandas', 'numpy'],
        'test': ['pytest', 'numpy', 'pandas', 'click'],
    },
    packages=setuptools.find_packages(),
    package_dir={'pyDO3SE': 'pyDO3SE'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    ext_modules=[
        # Extension('do3se._model', all_ext_files, ['config_fc', '--fcompiler=gnu95',
        #         '--f90flags="-fimplicit-none"', '--noopt'])
        Extension('do3se._model', buildpyf(ext_files, ext_name))
    ],
    data_files=[
        ('Microsoft.VC90.CRT',
         glob('resources/Microsoft.VC90.CRT/*')),
    ],
)
