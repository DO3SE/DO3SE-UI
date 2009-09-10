from dose_f import *

#
# Define available fields
#

# Available input fields in (module, variable, type, required, shortname, longname) format
_input_fields = (
        (inputs,    'yr',       int,    False,  'Year',         'Year'),
        (inputs,    'mm',       int,    False,  'Month',        'Month'),
        (inputs,    'mdd',      int,    False,  'Month day',    'Day of month'),
        (inputs,    'dd',       int,    True,   'Day',          'Day of year'),
        (inputs,    'hr',       int,    True,   'Hour',         'Hour of day (0 to 23)'),
        (inputs,    'ts_c',     float,  True,   'Ts_C (C)',     'Temperature (Ts_C, Celcius)'),
        (inputs,    'vpd',      float,  True,   'VPD (kPa)',    'Vapour Pressure Deficit (VPD, kPa)'),
        (inputs,    'uh_zr',    float,  True,   'uh_zR (m/s)',  'Measured wind speed (uh_zR, m/s)'),
        (inputs,    'precip',   float,  True,   'precip (mm)',  'Precipitation (precip, mm)'),
        (inputs,    'p',        float,  True,   'P (kPa)',      'Pressure (P, kPa)'),
        (inputs,    'o3_ppb_zr',float,  True,   'O3_zR (ppb)',  'Measured O3 density (O3_zR, ppb)'),
        (inputs,    'hd',       float,  False,  'Hd (Wh/m^2)',  'Sensible heat flux (Hd, Wh/m^2)'),
        (inputs,    'r',        float,  False,  'R (Wh/m^2)',   'Global radiation (Wh/m^2)'),
        (inputs,    'par',      float,  False,  'PAR (umol/m^2/s)', 'Photosynthetically active radiation (PAR, umol/m^2/s)'),
        (inputs,    'rn',       float,  False,  'Rn (Wh/m^2)',  'Net radiation (Rn, Wh/m^2)'),
)

# Available input fields as a list of dicts
input_fields = [{'module':      x[0],
                 'variable':    x[1],
                 'type':        x[2],
                 'required':    x[3],
                 'short':       x[4],
                 'long':        x[5]} for x in _input_fields]

# Mapping from input field variable name to full field info
input_field_map = dict( (x['variable'], x) for x in input_fields )

# Available output fields in (module, variable, type, shortname, longname) format
_output_fields = (
        # Inputs
        (inputs,        'yr',       int,    'Year',             'Year'),
        (inputs,        'mm',       int,    'Month',            'Month'),
        (inputs,        'mdd',      int,    'Month day',        'Day of month'),
        (inputs,        'dd',       int,    'Day',              'Day of year'),
        (inputs,        'hr',       int,    'Hour',             'Hour of day (0 to 23)'),
        (inputs,        'ts_c',     float,  'Ts_C (C)',         'Temperature (Ts_C, Celcius)'),
        (inputs,        'vpd',      float,  'VPD (kPa)',        'Vapour Pressure Deficit (VPD, kPa)'),
        (inputs,        'uh_zr',    float,  'uh_zR (m/s)',      'Measured wind speed (uh_zR, m/s)'),
        (inputs,        'precip',   float,  'precip (mm)',      'Precipitation (precip, mm)'),
        (inputs,        'p',        float,  'P (kPa)',          'Pressure (P, kPa)'),
        (inputs,        'o3_ppb_zr',float,  'O3_zR (ppb)',      'Measured O3 density (O3_zR, ppb)'),
        (inputs,        'hd',       float,  'Hd (Wh/m^2)',      'Sensible heat flux (Hd, Wh/m^2)'),
        (inputs,        'r',        float,  'R (Wh/m^2)',       'Global radiation (Wh/m^2)'),
        (inputs,        'par',      float,  'PAR (umol/m^2/s)', 'Photosynthetically active radiation (PAR, umol/m^2/s)'),

        # Calculated variables
        (inputs,        'ustar',    float,  'u* (m/s)',         'Friction velocity (u*, m/s)'),
        (variables,     'rn',       float,  'Rn (MJ/m^2/h)',    'Net radiation (Rn, MJ/m^2/h)'),
        (variables,     'rn_w',     float,  'Rn_W (Wh/m^2)',    'Net radiation (Rn, Wh/m^2)'),
        (variables,     'ra',       float,  'Ra (s/m)',         'Aerodynamic resistance (Ra, s/m)'),
        (variables,     'rb',       float,  'Rb (s/m)',         'Boundary layer resistance (Rinc, s/m)'),
        (variables,     'rsur',     float,  'Rsur (s/m)',       'Surface resistance (Rsur, s/m)'),
        (variables,     'rinc',     float,  'Rinc (s/m)',       'In-canopy resistance (Rinc, s/m)'),
        (variables,     'rsto',     float,  'Rsto (s/m)',       'Stomatal resistance (Rsto, s/m)'),
        (variables,     'gsto',     float,  'Gsto (mmol/m^2/s)','Stomatal conductance (Gsto, mmol/m^2/s)'),
        (variables,     'rgs',      float,  'Rgs (s/m)',        'Ground surface resistance (Rgs, s/m)'),
        (variables,     'vd',       float,  'Vd (m/s)',         'Deposition velocity (Vd, m/s)'),
        (variables,     'o3_ppb',   float,  'O3 (ppb)',         'Ozone concentration at canopy (O3, ppb)'),
        (variables,     'o3_nmol_m3',float, 'O3 (nmol/m^3)',    'Ozone concentration at canopy (O3, nmol/m^3)'),
        (variables,     'fst',      float,  'Fst (nmol/m^2/s)', 'Upper leaf stomatal O3 flux (Fst, nmol/m^2/s)'),
        (variables,     'afsty',    float,  'AFstY (nmol/m^2/s)','Accumulated Fst over threshold (AFstY, nmol/m^2/s)'),
        (variables,     'ftot',     float,  'Ftot (nmol/m^2/s)','Total ozone flux (Ftot, nmol/m^2/s)'),
        (variables,     'ot40',     float,  'OT40 (ppb)',       'Ozone over 40 ppb (OT40, ppb)'),
        (variables,     'aot40',    float,  'AOT40 (ppb)',      'Accumulated OT40 over growth period (AOT40, ppb)'),
        (variables,     'aet',      float,  'AEt (???)',        'Actual evapotranspiration (AEt, ???)'),
        (variables,     'swp',      float,  'SWP (MPa)',        'Soil water potential (SWP, MPa)'),
        (variables,     'per_vol',  float,  'per_vol (%)',      'Volumetric water content (per_vol, %)'),
        (variables,     'smd',      float,  'SMD (m)',          'Soil moisture deficit (SMD, m)'),

        # Debug variables
        (variables,     'ra_i',     float,  'Ra_i (s/m)',       '[DEBUG] Ra at O3 measurement'),
        (variables,     'eact',     float,  'eact',             '[DEBUG] eact'),
        (variables,     'lai',      float,  'LAI',              '[DEBUG] LAI'),
        (variables,     'sai',      float,  'SAI',              '[DEBUG] SAI'),
        (variables,     'flight',   float,  'flight',           '[DEBUG] flight'),
        (variables,     'ftemp',    float,  'ftemp',            '[DEBUG] ftemp'),
        (variables,     'fvpd',     float,  'fVPD',             '[DEBUG] fVPD'),
        (variables,     'fswp',     float,  'fSWP',             '[DEBUG] fSWP'),
        (variables,     'sinb',     float,  'sinB',             '[DEBUG] sinB'),
        (variables,     'ppardir',  float,  'pPARdir',          '[DEBUG] pPARdir'),
        (variables,     'ppardif',  float,  'pPARdiff',         '[DEBUG] pPARdiff'),
        (variables,     'fpardir',  float,  'fPARdir',          '[DEBUG] fPARdir'),
        (variables,     'fpardif',  float,  'fPARdiff',         '[DEBUG] fPARdiff'),
        (variables,     'laisun',   float,  'LAIsun',           '[DEBUG] LAIsun'),
        (variables,     'laishade', float,  'LAIshade',         '[DEBUG] LAIshade'),
        (variables,     'parsun',   float,  'PARsun',           '[DEBUG] PARsun'),
        (variables,     'parshade', float,  'PARshade',         '[DEBUG] PARshade'),

        (variables,     'rb_h2o',   float,  'Rb_H2O (s/m)',     '[DEBUG] Rb_H2O (boundary resistance to water)'),
        (variables,     'asw',      float,  'ASW',              '[DEBUG] ASW'),
        (variables,     'sn',       float,  'Sn',               '[DEBUG] Sn'),
        (variables,     'sn_diff',  float,  'Sn_diff',          '[DEBUG] Sn_diff'),
        (variables,     'ei',       float,  'Ei',               '[DEBUG] Ei'),
        (variables,     'es',       float,  'Es',               '[DEBUG] Es'),
        (variables,     'pet',      float,  'PEt',              '[DEBUG] PEt'),
        (variables,     'rsto_pet', float,  'Rsto_PEt',         '[DEBUG] Rsto_PEt'),
        (variables,     'precip_acc',float, 'precip_acc',       '[DEBUG] Accumulated precipitation (precip_acc, m)'),
        (variables,     'ei_hr',    float,  'Ei_hr',            '[DEBUG] Ei_hr'),
        (variables,     'es_hr',    float,  'Es_hr',            '[DEBUG] Es_hr'),
        (variables,     'pet_hr',   float,  'PEt_hr',           '[DEBUG] PEt_hr'),
        (variables,     'aet_hr',   float,  'AEt_hr',           '[DEBUG] AEt_hr'),
        (variables,     'pet_3',    float,  'PEt_3',            '[DEBUG] PEt_3'),
        (variables,     'aet_3',    float,  'AEt_3',            '[DEBUG] AEt_3'),
)

# Available output fields as a list of dicts
output_fields = [{'module':      x[0],
                  'variable':    x[1],
                  'type':        x[2],
                  'short':       x[3],
                  'long':        x[4]} for x in _output_fields]

# Mapping from output field variable name to full field info
output_field_map = dict( (x['variable'], x) for x in output_fields )

# Soil class data in (id, name, data) format
_soil_classes = (
        ('sand_loam',   'Sandy Loam (coarse)', {
            'soil_b':   3.31,
            'fc_m':     0.16,
            'swp_ae':   -0.00091,
        }),
        ('silt_loam',   'Silt loam (medium coarse)', {
            'soil_b':   4.38,
            'fc_m':     0.26,
            'swp_ae':   -0.00158,
        }),
        ('loam',        'Loam (medium)', {
            'soil_b':   6.58,
            'fc_m':     0.29,
            'swp_ae':   -0.00188,
        }),
        ('clay_loam',   'Clay loam (fine)', {
            'soil_b':   7.00,
            'fc_m':     0.37,
            'swp_ae':   -0.00588,
        }),
)

# Soil classes as a list of dicts
soil_classes = [{'id':      x[0],
                 'name':    x[1],
                 'data':    x[2]} for x in _soil_classes]

# Mapping from soil class id to full info
soil_class_map = dict( (x['id'], x) for x in soil_classes )

default_soil_class = 'loam'


def extract_outputs():
    """
    Extract all output variables

    Extract a dict containing the values of all of the variables defined in
    output_fields.
    """
    return dict( (x['variable'], x['type'](getattr(x['module'], x['variable']))) for x in output_fields )
