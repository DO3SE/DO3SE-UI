import os, shutil
import cPickle as pickle
from tools import _verbose

# Use Windows-specific paths if on Windows, otherwise use standard UNIX paths
if os.name == 'nt':
    settings_dir = os.path.join(os.environ['APPDATA'], '.do3se')
else:
    settings_dir = os.path.join(os.environ['HOME'], '.do3se')
_verbose("Found settings directory: " + settings_dir)

# Create the settings directory and copy default data to it if it doesn't exist
if not os.path.exists(settings_dir):
    os.mkdir(settings_dir)
    _verbose("Settings directory does not exist... creating!")

def _get_path(filename):
    """Utility function for getting full path to settings files."""
    return os.path.join(settings_dir, filename)

def _load_settings(filename):
    """Utility function for loading saved settings data.

    Loads a settings file and passes it through the depickler to retrieve the 
    data.
    """
    # Get the absolute path to the file
    path = _get_path(filename)
    _verbose('Loading data from %s ...' % path)

    # Copy defaults if the file doesn't exist yet
    if not os.path.exists(path):
        _verbose("%s does not exist - copying defaults from %s.default" % \
                (filename, filename))
        shutil.copy('defaults/%s.default' % filename, path)

    # Open the file in read-only binary mode
    file = open(path, 'rb')

    # Unpickle the data, give a more useful error message if the file is invalid
    try:
        data = pickle.load(file)
        file.close()
        return data
    except pickle.UnpicklingError:
        _verbose("%s contains invalid data!")
        raise

def _dump_settings(filename, obj):
    path = _get_path(filename)
    _verbose('Writing data to %s' % path)

    try:
        file = open(path, 'wb')
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)
        file.close()
    except IOError:
        _verbose('Failed to open %s for writing' % path)
        raise

state = _load_settings('state.pickle')
#sites = _load_settings('sites.pickle')
#species = _load_settings('species.pickle')


def Write():
    _dump_settings('state.pickle', state)

def GetRecentFiles():
    return state['recentfiles']

def AddRecentFile(path):
    """Add a path to the recent file list.

    The recent file list is maintained in reverse chronological order by most
    recent access, and limited to 10 items.
    """
    try:
        x = state['recentfiles'].index(path)
        state['recentfiles'] = [path] + state['recentfiles'][:x] + state['recentfiles'][x+1:]
    except:
        state['recentfiles'].insert(0, path)

    state['recentfiles'] = state['recentfiles'][:10]

def RemoveRecentFile(path):
    if path in state['recentfiles']:
        state['recentfiles'].remove(path)
