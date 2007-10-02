#!/usr/bin/env python

import cPickle as pickle

import maps

state = {}
state['recentfiles'] = []
state['formats'] = {}
state['formats']['input'] = {
        'Baum_DOSE original': [maps.input_fields[x] for x in 
            'mm mdd dd hr ts_c vpd precip uh o3_ppb_zr idrctt idfuse zen'.split()]
        }
state['formats']['output'] = {}

f = open('defaults/state.pickle.default', 'wb')
pickle.dump(state, f, pickle.HIGHEST_PROTOCOL)
