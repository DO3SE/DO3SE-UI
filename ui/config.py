defaults = {
    'file_history': list(),
    'input_fields': dict(),
    'output_fields': dict(),
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
    return JsonDict(filename, deepcopy(defaults))
