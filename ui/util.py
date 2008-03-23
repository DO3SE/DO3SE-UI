def setattrs(obj, d):
    for k,v in d.iteritems():
        setattr(obj, k, v)

def getattrs(obj, keys):
    return dict([(k, getattr(obj, k)) for k in keys])

def getattrs_f(obj, keys):
    return dict([(k, float(getattr(obj, k))) for k in keys])

def getattrs_i(obj, keys):
    return dict([(k, int(getattr(obj, k))) for k in keys])

def dictjoin(*args):
    d = dict()
    for a in args: d.update(a)
    return d

def versioncmp(v1, v2):
    return [int(x) for x in v1.split('.')] > [int(x) for x in v2.split('.')]
