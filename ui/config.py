defaults = {
    'file_history': list(),
    'input_format': dict(),
    'output_format': dict(),
    'site_params': dict(),
    'veg_params': {
        'Coniferous Forests (CF)': {
            'gmax': 160,
            'fmin': 0.1,
        },
        'Deciduous Forests (DF)': {
            'gmax': 134,
            'fmin': 0.13,
        },
        'Needleleaf Forests (NF)': {
            'gmax': 180,
            'fmin': 0.13,
        },
        'Broadleaf Forests (BF)': {
            'gmax': 200,
            'fmin': 0.03,
        },
    },
}

from jsondict import JsonDict
from copy import deepcopy

def open_config(filename):
    """
    Open a JSON file as a dict
    """
    return JsonDict(filename, deepcopy(defaults))

import dose

def sanitise_config(config):
    """
    Sanitise a configuration dict

    Perform little cleanups like removing references to fields that don't exist
    """
    # Remove references to non-existant input fields
    for key, preset in config['input_format'].iteritems():
        config['input_format'][key] = [x for x in preset if x in input_field_map]
    # Remove references to non-existant output fields
    for key, preset in config['output_format'].iteritems():
        config['output_format'][key] = [x for x in preset if x in output_field_map]
