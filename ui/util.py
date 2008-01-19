def setattrs(obj, d):
    for k,v in d.iteritems():
        setattr(obj, k, v)

def getattrs(obj, keys):
    return dict([(k, getattr(obj, k)) for k in keys])

def getattrs_f(obj, keys):
    return dict([(k, float(getattr(obj, k))) for k in keys])
