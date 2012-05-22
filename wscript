#!/usr/bin/env python

def options(ctx):
    ctx.recurse('do3se_core')


def configure(ctx):
    ctx.recurse('do3se_core')


def build(ctx):
    ctx.recurse('do3se_core')
