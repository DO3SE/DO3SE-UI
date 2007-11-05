import cPickle as pickle

import maps

state = {}
state['recentfiles'] = []
state['presets'] = {}
state['presets']['input'] = {}
state['presets']['output'] = {}
state['presets']['site'] = {}

f = open('defaults/state.pickle.default', 'wb')
pickle.dump(state, f, pickle.HIGHEST_PROTOCOL)
