import logging
_log = logging.getLogger('do3se.util.picklefile')
import tempfile
import shutil
import os
import os.path
try:
    import cPickle as pickle
    _log.debug('Using cPickle =D')
except ImportError:
    import pickle
    _log.debug('Using plain pickle =(')


class PickleFile:
    """
    A lazy wrapper for storing an object using the pickle interface.

    The purpose of this class is quite similar to the built-in :mod:`shelve`
    module, but differs in almost every way.
    
    The path to the pickle file and the object to be stored are exposed as the
    :attr:`filename` and :attr:`data` attributes respectively, and these are
    intended to be externally manipulated by other code.

    Unlike :mod:`shelve`, the use of a :class:`PickleFile` is "lazy", in that
    a filename isn't required until the point at which the pickle file is saved
    or explicitly (re)loaded.

    If the *filename* argument is supplied to the constructor and *autoload*
    is True, then the contents of the file will be loaded.

    Generally speaking problems occurring within this class will result in
    either :class:`IOError` or :class:`OSError` exceptions (and can therefore
    be caught as :class:`EnvironmentError`).
    """
    def __init__(self, filename=None, autoload=False):
        self.filename = filename

        if autoload:
            self.load()

    def save(self, filename=None):
        """
        Atomically save the pickle file.

        :attr:`data` is saved to the pickle file atomically, by first writing
        to a temporary file and then moving that to the correct location.
        This prevents an unexpected exception clobbering the existing file if
        there is one.

        If *filename* is supplied, it replaces the value of the :attr:`filename`
        attribute.
        """
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename

        if filename is None:
            raise IOError('No filename set')

        # Any IOError from here will escape to the caller
        (fd, tmpfilename) = tempfile.mkstemp(prefix=os.path.basename(filename) + '.tmp',
                                             dir=os.path.dirname(filename))
        f = os.fdopen(fd, 'wb')
        _log.debug('Created temporary file ' + tmpfilename)
        pickle.dump(self.data, f)
        f.close()
        shutil.move(tmpfilename, filename)
        _log.debug('Saved ' + filename)

    def load(self, filename=None):
        """
        Load from the pickle file.

        The :attr:`data` attribute is replaced with the object from the pickle
        file.

        If *filename* is supplied, it replaces the value of the :attr:`filename`
        attribute.
        """
        if filename is None:
            filename = self.filename
        else:
            self.filename = filename

        if filename is None:
            raise IOError('No filename set')

        f = open(filename, 'rb')
        try:
            self.data = pickle.load(f)
        except:
            raise IOError('Invalid pickle file')
        finally:
            f.close()

        _log.debug('Loaded ' + filename)
