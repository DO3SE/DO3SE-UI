import sys

VERBOSE = True

def _verbose(msg):
    if VERBOSE:
        sys.stderr.write(msg + '\n')

def truedict(obj):
    ret = {}
    for k in obj.__dict__.keys():
        ret[k] = getattr(obj, k)
    return ret
