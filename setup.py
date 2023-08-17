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
# from do3se.version import app_version, app_name
with open("README.md", "r") as fh:
    long_description = fh.read()

root = os.environ['BUILD_ROOT'] # This is a hack to fix missing objects.mk issue
app_name = 'do3se'
app_description = 'Deposition of Ozone and Stomatal Exchange'
app_version = '3.6.31'
fortran_src_dir = 'src/F'

ext_files = [os.path.join(fortran_src_dir, x) for x in
             re.findall(r'\w+\.f90',
                        re.sub(r'(\w+)\.o', r'\1.f90',
                               open(os.path.join(root, fortran_src_dir, 'objects.mk'), 'r').read()))]

all_ext_files = ['src/do3se/_model.pyf'] + ext_files

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

ext = Extension('do3se._model', buildpyf(ext_files, ext_name))

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
    ],
    extras_require={
        'cli': ['pytest', 'numpy', 'pandas', 'click'],
        'grid': ['xarray', 'netCDF4', 'pandas', 'numpy'],
        'test': ['pytest', 'numpy', 'pandas', 'click'],
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    ext_modules=[
        # Extension('do3se._model', all_ext_files, ['config_fc', '--fcompiler=gnu95',
        #         '--f90flags="-fimplicit-none"', '--noopt'])
        ext,
    ],
    data_files=[
        ('Microsoft.VC90.CRT',
         glob('resources/Microsoft.VC90.CRT/*')),
    ],
)
