#!/usr/bin/env python

import sys
import pprint

from do3se.project import Project

if __name__ == '__main__':
    p = Project(sys.argv[1])
    pprint.pprint(dict(p.data))
