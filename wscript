#!/usr/bin/env python

APPNAME = 'do3se'
VERSION = '1.0'

def options(ctx):
    ctx.load('compiler_c')
    ctx.load('compiler_fc')


def configure(ctx):
    ctx.load('compiler_c')
    ctx.load('compiler_fc')
    ctx.check_fortran()
    ctx.env.FCFLAGS_DO3SE = ['-std=f95', '-fimplicit-none', '-fPIC', '-Wall']


def build(ctx):
    ctx(features='fc fcstlib',
        source=ctx.path.ant_glob('*.f90'),
        target=APPNAME,
        use='DO3SE')