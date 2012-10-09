#!/usr/bin/env python

def options(ctx):
    ctx.recurse('do3se_core')


def configure(ctx):
    ctx.recurse('do3se_core')


def build(ctx):
    ctx.recurse('do3se_core')
    ctx.recurse('do3se_model')
    ctx(features='fc fcprogram',
        source=ctx.path.ant_glob('F/*.f90'),
        target='run_do3se',
        use='do3se',
        fcflags=['-fimplicit-none', '-fPIC', '-Wall'])
