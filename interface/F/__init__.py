#!/usr/bin/python

from do3se import *

def SetSiteParam(param, value):
    setattr(params_site, param, value)

def SetVegParam(param, value):
    setattr(params_veg, param, value)
