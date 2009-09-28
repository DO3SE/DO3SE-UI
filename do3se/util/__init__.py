def setattrs(obj, d):
    for k,v in d.iteritems():
        setattr(obj, k, v)
