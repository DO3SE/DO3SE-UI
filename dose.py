from dose_f import *

def SetSiteParams(params):
    for k, v in params.iteritems():
        setattr(params_site, k, v)

def SetVegParams(params):
    for k, v in params.iteritems():
        setattr(params_veg, k, v)

def SetInputValues(values):
    for k, v in values.iteritems():
        setattr(inputs, k, float(v))

def GetValues(keys):
    data = {}
    for k in keys:
        data[k] = float(getattr(variables, k))
    return data

def GetAllValues():
    data = {}
    for k in variables.__dict__.keys():
        data[k] = float(getattr(variables, k))
    return data
