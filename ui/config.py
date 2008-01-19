################################################################################
# Configuration file handler
#
# Uses Python's useful 'shelve' module to make a file-backed auto-saving 
# dictionary.  Also give some helper functions for common tasks for the DOSE
# configuration file.
################################################################################

import shelve
import os
from util import logging

# Get the OS-dependant path to use for the configuration file
if os.name == 'nt':
    configpath = os.path.join(os.environ['APPDATA'], 'DOSE', 'dose.cfg')
else:
    configpath = os.path.join(os.environ['HOME'], '.DOSE', 'dose.cfg')
logging.info("Using configuration file '%s'" % configpath)

# Create the directory if necessary
if not os.path.exists(os.path.dirname(configpath)):
    os.mkdir(os.path.dirname(configpath))
    logging.debug("Created directory '%s'" % os.path.dirname(configpath))

# Open the config file
config = shelve.open(configpath)

# If the config is empty, it's just been created, so set up the default config
if len(config) == 0:
    config['filehistory'] = []
    logging.debug("Created default configuration")


def add_recent_file(path):
    """Add a path to recent file history

    Adds the path to the file history list, removing duplicates and making sure
    the list is only 9 items long and in chronological order.
    """
    d = config['filehistory']
    try:
        d.remove(path)
    except ValueError:
        pass
    d.append(path)
    d = d[-9:]
    config['filehistory'] = d
