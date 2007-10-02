import sys

VERBOSE = True

def _verbose(msg):
    if VERBOSE:
        sys.stderr.write(msg + '\n')
