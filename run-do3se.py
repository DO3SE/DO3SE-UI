#!/usr/bin/python

import sys
import logging

from do3se.application import App

if __name__ == '__main__':
    # If the app is frozen (i.e. made into an executable), don't annoy the user
    # with log messages they don't care about.
    if hasattr(sys, 'frozen') and sys.frozen:
        level = logging.CRITICAL
    else:
        level = logging.DEBUG
    logging.basicConfig(level=level, format='[%(levelname)-8s] %(message)s')

    # Run the application
    app = App()
    app.Run()
