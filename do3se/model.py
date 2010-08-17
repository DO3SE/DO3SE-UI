from do3se_fortran import *
from util import to_dicts, dicts_to_map, OrderedDict

#: Available input fields
input_fields = to_dicts(('module', 'variable', 'type', 'required', 'short', 'long'), (
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
        (inputs,    'rn',       float,  False,  'Rn (MJ/m^2)',  'Net radiation (Rn, MJ/m^2)'),
))

#: Mapping from input field variable name to full field info
input_field_map = dicts_to_map(input_fields, 'variable')

#: Available output fields
output_fields = to_dicts(('module', 'variable', 'type', 'short', 'long'), (
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
        (inputs,        'uh_i',     float,  'uh50 (m/s)',       'Wind speed at 50m (uh50, m/s)'),
        (inputs,        'uh',       float,  'uh (m/s)',         'Wind speed at target canopy (uh, m/s)'),
        (inputs,        'rn',       float,  'Rn (MJ/m^2)',      'Net radiation (Rn, MJ/m^2)'),
        (inputs,        'rn_w',     float,  'Rn_W (Wh/m^2)',    'Net radiation (Rn, Wh/m^2)'),
        (variables,     'ra',       float,  'Ra (s/m)',         'Aerodynamic resistance (Ra, s/m)'),
        (variables,     'rb',       float,  'Rb (s/m)',         'Boundary layer resistance (Rinc, s/m)'),
        (variables,     'rsur',     float,  'Rsur (s/m)',       'Surface resistance (Rsur, s/m)'),
        (variables,     'rinc',     float,  'Rinc (s/m)',       'In-canopy resistance (Rinc, s/m)'),
        (variables,     'rsto',     float,  'Rsto (s/m)',       'Mean stomatal resistance (Rsto, s/m)'),
        (variables,     'gsto',     float,  'Gsto (mmol/m^2/s)','Mean stomatal conductance (Gsto, mmol/m^2/s)'),
        (variables,     'rgs',      float,  'Rgs (s/m)',        'Ground surface resistance (Rgs, s/m)'),
        (variables,     'vd',       float,  'Vd (m/s)',         'Deposition velocity (Vd, m/s)'),
        (variables,     'o3_ppb_i', float,  'O350 (ppb)',       'Ozone concentration at 50m (O350, ppb)'),
        (variables,     'o3_ppb',   float,  'O3 (ppb)',         'Ozone concentration at canopy (O3, ppb)'),
        (variables,     'o3_nmol_m3',float, 'O3 (nmol/m^3)',    'Ozone concentration at canopy (O3, nmol/m^3)'),
        (variables,     'fst',      float,  'Fst (nmol/m^2/s)', 'Upper leaf stomatal O3 flux (Fst, nmol/m^2/s)'),
        (variables,     'afsty',    float,  'AFstY (nmol/m^2/s)','Accumulated Fst over threshold (AFstY, nmol/m^2/s)'),
        (variables,     'ftot',     float,  'Ftot (nmol/m^2/s)','Total ozone flux (Ftot, nmol/m^2/s)'),
        (variables,     'ot40',     float,  'OT40 (ppb)',       'Ozone over 40 ppb (OT40, ppb)'),
        (variables,     'aot40',    float,  'AOT40 (ppb)',      'Accumulated OT40 over growth period (AOT40, ppb)'),
        (variables,     'et',       float,  'Et (???)',         'Plant traspiration (Et, ???)'),
        (variables,     'swp',      float,  'SWP (MPa)',        'Soil water potential (SWP, MPa)'),
        (variables,     'per_vol',  float,  'per_vol (%)',      'Volumetric water content (per_vol, %)'),
        (variables,     'smd',      float,  'SMD (m)',          'Soil moisture deficit (SMD, m)'),
        (variables,     'lwp',      float,  'LWP (???)',        'Leaf water potential (LWP, ???)'),
        (variables,     'sn_meas',  float,  'Sn_meas',          'Sn_meas'),
        (variables,     'sn_diff_meas', float, 'Sn_diff_meas',  'Sn_diff_meas'),
        (variables,     'swp_meas', float,  'SWP_meas',         'SWP_meas'),
        (variables,     'smd_meas', float,  'SMD_meas',         'SMD_meas'),

        # Debug variables
        (variables,     'ra_i',     float,  'Ra_i (s/m)',       '[DEBUG] Ra at O3 measurement'),
        (variables,     'lai',      float,  'LAI',              '[DEBUG] LAI'),
        (variables,     'sai',      float,  'SAI',              '[DEBUG] SAI'),
        (variables,     'flight',   float,  'flight',           '[DEBUG] flight'),
        (variables,     'ftemp',    float,  'ftemp',            '[DEBUG] ftemp'),
        (variables,     'fvpd',     float,  'fVPD',             '[DEBUG] fVPD'),
        (variables,     'fswp',     float,  'fSWP',             '[DEBUG] fSWP'),
        (inputs,        'sinb',     float,  'sinB',             '[DEBUG] sinB'),
        (variables,     'ppardir',  float,  'pPARdir',          '[DEBUG] pPARdir'),
        (variables,     'ppardif',  float,  'pPARdiff',         '[DEBUG] pPARdiff'),
        (variables,     'fpardir',  float,  'fPARdir',          '[DEBUG] fPARdir'),
        (variables,     'fpardif',  float,  'fPARdiff',         '[DEBUG] fPARdiff'),
        (variables,     'laisun',   float,  'LAIsun',           '[DEBUG] LAIsun'),
        (variables,     'laishade', float,  'LAIshade',         '[DEBUG] LAIshade'),
        (variables,     'parsun',   float,  'PARsun',           '[DEBUG] PARsun'),
        (variables,     'parshade', float,  'PARshade',         '[DEBUG] PARshade'),

        (variables,     'leaf_flight',float,'leaf_flight',      '[DEBUG] leaf_flight'),
        (variables,     'fphen',    float,  'fphen',            '[DEBUG] fphen'),
        (variables,     'leaf_fphen',float, 'leaf_fphen',       '[DEBUG] leaf_fphen'),

        (variables,     'rsto_l',   float,  'Rsto_l (s/m)',       '[DEBUG] Leaf stomatal resistance (Rsto_l, s/m)'),
        (variables,     'gsto_l',   float,  'Gsto_l (mmol/m^2/s)','[DEBUG] Leaf stomatal conductance (Gsto_l, mmol/m^2/s)'),
        (variables,     'rsto_c',   float,  'Rsto_c (s/m)',       '[DEBUG] Canopy stomatal resistance (Rsto_c, s/m)'),
        (variables,     'gsto_c',   float,  'Gsto_c (mmol/m^2/s)','[DEBUG] Canopy stomatal conductance (Gsto_c, mmol/m^2/s)'),
        (variables,     'rsto_pet', float,  'Rsto_PEt (s/m)',       '[DEBUG] Rsto_PEt (Rsto_PEt, s/m)'),
        (variables,     'gsto_pet', float,  'Gsto_PEt (mmol/m^2/s)','[DEBUG] Gsto_PEt (Gsto_PEt, mmol/m^2/s)'),

        (variables,     'rb_h2o',   float,  'Rb_H2O (s/m)',     '[DEBUG] Rb_H2O (boundary resistance to water)'),
        (variables,     'fpaw',     float,  'fPAW',             '[DEBUG] fPAW'),
        (variables,     'asw',      float,  'ASW',              '[DEBUG] ASW'),
        (variables,     'sn',       float,  'Sn',               '[DEBUG] Sn'),
        (variables,     'p_input',  float,  'P_input',          '[DEBUG] P_input'),
        (variables,     'sn_diff',  float,  'Sn_diff',          '[DEBUG] Sn_diff'),
        (variables,     'ei',       float,  'Ei',               '[DEBUG] Ei'),
        (variables,     'es',       float,  'Es',               '[DEBUG] Es'),
        (variables,     'pet',      float,  'PEt',              '[DEBUG] Potential plant transpiration (PEt)'),
        (inputs,        'precip_acc',float, 'precip_acc',       '[DEBUG] Accumulated precipitation (precip_acc, m)'),
        (soilwater,     'ei_hr',    float,  'Ei_hr',            '[DEBUG] Ei_hr'),
        (soilwater,     'es_hr',    float,  'Es_hr',            '[DEBUG] Es_hr'),
        (soilwater,     'pet_hr',   float,  'PEt_hr',           '[DEBUG] PEt_hr'),
        (soilwater,     'et_hr',    float,  'Et_hr',            '[DEBUG] Et_hr'),
        (soilwater,     'pet_3',    float,  'PEt_3',            '[DEBUG] PEt_3'),
        (soilwater,     'et_3',     float,  'Et_3',             '[DEBUG] Et_3'),
        (variables,     'delta_lwp',float,  'delta_LWP',        '[DEBUG] delta_LWP'),
        (variables,     'flwp',     float,  'fLWP',             '[DEBUG] fLWP'),
        (variables,     'fxwp',     float,  'fXWP',             '[DEBUG] fXWP'),

        (variables,     'ot0',      float,  'OT0',              '[DEBUG] OT0'),
        (variables,     'aot0',     float,  'AOT0',             '[DEBUG] AOT0'),
        (variables,     'afst0',    float,  'AFst0',            '[DEBUG] Afst0'),
        (variables,     'fo3',      float,  'fO3',              '[DEBUG] fO3'),
))

#: Mapping from output field variable name to full field info
output_field_map = dicts_to_map(output_fields, 'variable')

#: Soil class data
soil_classes = dicts_to_map(to_dicts(('id', 'name', 'data'), (
    ('sand_loam',   'Sandy Loam (coarse)', {
        'soil_b':   3.31,
        'fc_m':     0.16,
        'swp_ae':   -0.00091,
        'ksat':     0.0009576,
    }),
    ('silt_loam',   'Silt loam (medium coarse)', {
        'soil_b':   4.38,
        'fc_m':     0.26,
        'swp_ae':   -0.00158,
        'ksat':     0.0002178,
    }),
    ('loam',        'Loam (medium)', {
        'soil_b':   6.58,
        'fc_m':     0.29,
        'swp_ae':   -0.00188,
        'ksat':     0.0002286,
    }),
    ('clay_loam',   'Clay loam (fine)', {
        'soil_b':   7.00,
        'fc_m':     0.37,
        'swp_ae':   -0.00588,
        'ksat':     0.00016,
    }),
)), 'id', OrderedDict)

#: Default soil class
default_soil_class = 'loam'

#: Leaf fphen calculations
leaf_fphen_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('copy',    switchboard.leaf_fphen_equals_fphen,    'Same as Fphen'),
    ('wheat',   switchboard.leaf_fphen_wheat,           'Wheat'),
    ('potato',  switchboard.leaf_fphen_potato,          'Potato'),
)), 'id', OrderedDict)

default_leaf_fphen_calc = 'copy'

# fO3 calculations
fO3_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('none',    switchboard.fo3_disabled,   'Not used (fO3 = 1)'),
    ('wheat',   switchboard.fo3_wheat,      'Wheat'),
    ('potato',  switchboard.fo3_potato,     'Potato'),
)), 'id', OrderedDict)

default_fO3_calc = 'none'

# SAI calculations
SAI_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('copy',    switchboard.sai_equals_lai, 'Same as LAI'),
    ('forest',  switchboard.sai_forest,     'Forest'),
    ('wheat',   switchboard.sai_wheat,      'Wheat'),
)), 'id', OrderedDict)

default_SAI_calc = 'copy'

# fXWP calculations (switching between fSWP, fLWP and neither)
fXWP_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('disabled',    switchboard.fxwp_disabled,  'Disabled'),
    ('fswp',        switchboard.fxwp_use_fswp,  'Use fSWP'),
    ('flwp',        switchboard.fxwp_use_flwp,  'Use fLWP'),
    ('fpaw',        switchboard.fxwp_use_fpaw,  'Use fPAW'),
)), 'id', OrderedDict)

default_fXWP_calc = 'disabled'

# fSWP calculations (switching between exponential and linear relationship
fSWP_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('exp',     switchboard.fswp_exponential,   'Exponential'),
    ('linear',  switchboard.fswp_linear,        'Linear (SWP_min, SWP_max)'),
)), 'id', OrderedDict)

default_fSWP_calc = 'exp'

# LWP calculations (steady-state and non-steady-state)
LWP_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('nss',     switchboard.lwp_non_steady_state, 'Non steady-state'),
    ('ss',      switchboard.lwp_steady_state,     'Steady-state'),
)), 'id', OrderedDict)

default_LWP_calc = 'nss'


def extract_outputs():
    """
    Extract all output variables

    Extract a dict containing the values of all of the variables defined in
    output_fields.
    """
    return dict( (x['variable'], x['type'](getattr(x['module'], x['variable']))) for x in output_fields )
