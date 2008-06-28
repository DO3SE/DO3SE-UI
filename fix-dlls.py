#!/usr/bin/env python

import os.path, glob, wx, shutil, sys

wxpath = os.path.dirname(wx.__file__)
distpath = sys.argv[1]

dlls = glob.glob(os.path.join(wxpath, "msvcp??.dll")) \
        + [os.path.join(wxpath, "gdiplus.dll")]

for dll in dlls:
    print "Copying %s to %s" % (dll, distpath)
    shutil.copy(dll, distpath)
