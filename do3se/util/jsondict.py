try:
    import json
except ImportError:
    import simplejson as json

import os, shutil

class JsonDict(dict):
    """
    Dictionary backed by a JSON file

    A dictionary class using a JSON file as storage, but without automatic
    syncronisation.  Writes are atomic, and the implementation borrows very
    heavily from: http://code.activestate.com/recipes/576642/

    If the file doesn't already exist, it will be created.
    """

    def __init__(self, filename, *args, **kwargs):
        """
        Load initial data
        """
        self.filename = filename

        # Use other arguments as defaults
        self.update(*args, **kwargs)

        # Attempt to read the file if it's readable
        if os.access(filename, os.R_OK):
            file = open(self.filename, 'r')
            try:
                self.load(file)
            finally:
                file.close()


    def load(self, file):
        """
        Load data from JSON file
        """
        file.seek(0)
        try:
            return self.update(json.load(file))
        except Exception:
            raise ValueError('File not in recognised JSON format')


    def dump(self, file):
        """
        Dump data to a JSON file (pretty-printed)
        """
        json.dump(self, file, indent=4)


    def sync(self):
        """
        Syncronise file with in-memory data
        """
        tempname = self.filename + '.tmp'
        file = open(tempname, 'w')

        try:
            self.dump(file)
        except:
            file.close()
            os.remove(tempname)
            raise

        file.close()
        # Atomic commit
        shutil.move(tempname, self.filename)


    def close(self):
        """
        Sync on close
        """
        self.sync()
