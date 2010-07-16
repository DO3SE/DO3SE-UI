#!/usr/bin/python

#
# Setup logging
#
import sys, logging
# Default log level
level = logging.DEBUG
# See if we're running "frozen" - if so, don't annoy the user with pointless
# debug messages
try:
    if sys.frozen:
        level = logging.CRITICAL
except AttributeError:
    pass
# Initialise logger
logging.basicConfig(level=level, format='[%(levelname)-8s] %(message)s')


#
# Run the application
#
from do3se.application import App
app = App()
app.Run()
