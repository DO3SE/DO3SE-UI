#!/usr/bin/env python

import cPickle as pickle

state = {}
state['recentfiles'] = []
state['formats'] = {}
state['formats']['input'] = {'Baum_DOSE original': ['mm', 'mdd', 'dd', 'hr', 'ts_c', 'vpd', 'precip', 
        'uh', 'o3_ppb_zr', 'idrctt', 'idfuse', 'zen']}
state['formats']['output'] = {}

f = open('defaults/state.pickle.default', 'wb')
pickle.dump(state, f, pickle.HIGHEST_PROTOCOL)
