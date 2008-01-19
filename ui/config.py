################################################################################
# Configuration file handler
#
# Use Python's useful 'shelve' module to make a file-backed auto-saving 
# dictionary.  Also give some helper functions for common tasks for the DOSE
# configuration file.
################################################################################

import shelve

# Insert code here to work out the correct path to the configuration file based
# on the host operating system.

config = shelve.open('dose.cfg')

# Insert code here to create a default config if it's empty

def add_recent_file(path):
    d = config['filehistory']
    try:
        d.remove(path)
    except ValueError:
        pass
    d.append(path)
    d = d[-9:]
    config['filehistory'] = d

def reset():
    config['filehistory'] = []
