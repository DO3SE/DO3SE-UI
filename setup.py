"""This is a WIP updated setup file.

TODO:
- Bring in manifest
- Build fortran
- Implement py2exe

"""
import setuptools
from glob import glob
from do3se import application

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=application.app_name,
    version=application.app_version,
    author='Sam Bland | Alan Briolat',
    author_email='sam.bland@sei.org | alan.briolat@sei-international.org',
    description="DO3SE model python API",
    extras_require={'cli': ['pytest', 'numpy', 'pandas']},
    packages=setuptools.find_packages(),
    package_dir={'pyDO3SE': 'pyDO3SE'},
    install_require=['numpy', 'future'],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    data_files=[
        ('Microsoft.VC90.CRT',
         glob('resources/Microsoft.VC90.CRT/*')),
    ],
)
