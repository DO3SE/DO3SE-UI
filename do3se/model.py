# coding: utf-8
from _model import *
from util import to_dicts, dicts_to_map, OrderedDict
from fields import SpinField, FloatSpinField, ChoiceField, disableable

#: Available input fields
input_fields = dicts_to_map(to_dicts(('module', 'variable', 'type', 'required', 'short', 'long'), (
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
        (inputs,    'hd',       float,  False,  'Hd (Wh/m^2)',  u'Sensible heat flux (Hd, Wh/m\u00b2)'),
        (inputs,    'r',        float,  False,  'R (Wh/m^2)',   u'Global radiation (R, Wh/m\u00b2)'),
        (inputs,    'par',      float,  False,  'PAR (umol/m^2/s)', u'Photosynthetically active radiation (PAR, umol/m\u00b2/s)'),
        (inputs,    'rn',       float,  False,  'Rn (MJ/m^2)',  u'Net radiation (Rn, MJ/m\u00b2)'),
        (inputs,    'leaf_fphen_input', float, False, 'Leaf fphen', 'Leaf fphen'),
)), 'variable', OrderedDict)

#: Available output fields
output_fields = dicts_to_map(to_dicts(('module', 'variable', 'type', 'short', 'long'), (
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
        (inputs,        'precip_acc',float, 'precip_acc',       'Accumulated precipitation (precip_acc, m)'),
        (inputs,        'p',        float,  'P (kPa)',          'Pressure (P, kPa)'),
        (inputs,        'o3_ppb_zr',float,  'O3_zR (ppb)',      'Measured O3 density (O3_zR, ppb)'),
        (inputs,        'hd',       float,  'Hd (Wh/m^2)',      u'Sensible heat flux (Hd, Wh/m\u00b2)'),
        (inputs,        'r',        float,  'R (Wh/m^2)',       u'Global radiation (R, Wh/m\u00b2)'),
        (inputs,        'par',      float,  'PAR (umol/m^2/s)', u'Photosynthetically active radiation (PAR, umol/m\u00b2/s)'),

        # Calculated variables
        (inputs,        'ustar',    float,  'u* (m/s)',         'Friction velocity (u*, m/s)'),
        (inputs,        'uh_i',     float,  'uh50 (m/s)',       'Wind speed at 50m (uh50, m/s)'),
        (inputs,        'uh',       float,  'uh (m/s)',         'Wind speed at target canopy (uh, m/s)'),
        (inputs,        'rn',       float,  'Rn (MJ/m^2)',      u'Net radiation (Rn, MJ/m\u00b2)'),
        (inputs,        'rn_w',     float,  'Rn_W (Wh/m^2)',    u'Net radiation (Rn, Wh/m\u00b2)'),
        (variables,     'ra',       float,  'Ra (s/m)',         'Aerodynamic resistance (Ra, s/m)'),
        (variables,     'rb',       float,  'Rb (s/m)',         'Boundary layer resistance (Rinc, s/m)'),
        (variables,     'rsur',     float,  'Rsur (s/m)',       'Surface resistance (Rsur, s/m)'),
        (variables,     'rinc',     float,  'Rinc (s/m)',       'In-canopy resistance (Rinc, s/m)'),
        (variables,     'rsto',     float,  'Rsto (s/m)',       'Mean stomatal resistance (Rsto, s/m)'),
        (variables,     'gsto',     float,  'Gsto (mmol/m^2/s)',u'Mean stomatal conductance (Gsto, mmol/m\u00b2/s)'),
        (variables,     'rsto_l',   float,  'Rsto_l (s/m)',       'Leaf stomatal resistance (Rsto_l, s/m)'),
        (variables,     'gsto_l',   float,  'Gsto_l (mmol/m^2/s)',u'Leaf stomatal conductance (Gsto_l, mmol/m\u00b2/s)'),
        (variables,     'rsto_c',   float,  'Rsto_c (s/m)',       'Canopy stomatal resistance (Rsto_c, s/m)'),
        (variables,     'gsto_c',   float,  'Gsto_c (mmol/m^2/s)',u'Canopy stomatal conductance (Gsto_c, mmol/m\u00b2/s)'),
        (variables,     'rgs',      float,  'Rgs (s/m)',        'Ground surface resistance (Rgs, s/m)'),
        (variables,     'vd',       float,  'Vd (m/s)',         'Deposition velocity (Vd, m/s)'),
        (variables,     'o3_ppb_i', float,  'O350 (ppb)',       'Ozone concentration at 50m (O350, ppb)'),
        (variables,     'o3_ppb',   float,  'O3 (ppb)',         'Ozone concentration at canopy (O3, ppb)'),
        (variables,     'o3_nmol_m3',float, 'O3 (nmol/m^3)',    u'Ozone concentration at canopy (O3, nmol/m\u00b3)'),
        (variables,     'fst',      float,  'Fst (nmol/m^2/s)', u'Upper leaf stomatal O3 flux (Fst, nmol/m\u00b2/s)'),
        (variables,     'afst0',    float,  'POD0 (mmol/m^2 PLA)',u'Accumulated Fst (POD0, mmol/m\u00b2 PLA)'),
        (variables,     'afsty',    float,  'PODY (mmol/m^2 PLA)',u'Accumulated Fst over threshold Y (PODY, mmol/m\u00b2 PLA)'),
        (variables,     'ftot',     float,  'Ftot (nmol/m^2/s)',u'Total ozone flux (Ftot, nmol/m\u00b2/s)'),
        (variables,     'ot40',     float,  'OT40 (ppm)',       'Ozone over 40 ppb (OT40, ppm)'),
        (variables,     'aot40',    float,  'AOT40 (ppm)',      'Accumulated OT40 over growth period (AOT40, ppm)'),

        (variables,     'lai',      float,  'LAI',              u'Leaf Area Index (LAI, m\u00b2/m\u00b2)'),
        (variables,     'sai',      float,  'SAI',              u'Stand Area Index (SAI, m\u00b2/m\u00b2)'),

        (variables,     'pet',      float,  'PEt (m/day)',      'Potential plant transpiration (PEt, m/day)'),
        (variables,     'et',       float,  'Et (m/day)',       'Plant traspiration (Et, m/day)'),
        (variables,     'ei',       float,  'Ei (m/day)',       'Evaporation of intercepted precipitation (Ei, m/day)'),
        (variables,     'es',       float,  'Es (m/day)',       'Soil evaporation (Es, m/day)'),
        (variables,     'sn',       float,  'Sn (m^3/m^3)',     u'Soil water content (Sn, m\u00b3/m\u00b3)'),
        (variables,     'per_vol',  float,  'per_vol (%)',      'Volumetric water content (per_vol, %)'),
        (variables,     'smd',      float,  'SMD (m)',          'Soil moisture deficit (SMD, m)'),
        (variables,     'swp',      float,  'SWP (MPa)',        'Soil water potential (SWP, MPa)'),
        (variables,     'lwp',      float,  'LWP (MPa)',        'Leaf water potential (LWP, MPa)'),
        (variables,     'asw',      float,  'ASW (m^3/m^3)',    u'Available soil water (ASW, m\u00b3/m\u00b3)'),

        (variables,     'sn_meas',  float,  'Sn_meas (m^3/m^3)',u'Soil water content at measurement depth (Sn_meas, m\u00b3/m\u00b3)'),
        (variables,     'swp_meas', float,  'SWP_meas (MPa)',   'Soil water potential at measurement depth (SWP_meas, MPa)'),
        (variables,     'smd_meas', float,  'SMD_meas (m)',     'Soil moisture deficit at measurement depth (SMD_meas, m)'),

        # Debug variables
        #(variables,     'flight',   float,  'flight',           '[DEBUG] flight'),
        #(variables,     'leaf_flight',float,'leaf_flight',      '[DEBUG] leaf_flight'),
        #(variables,     'fphen',    float,  'fphen',            '[DEBUG] fphen'),
        #(variables,     'leaf_fphen',float, 'leaf_fphen',       '[DEBUG] leaf_fphen'),
        #(variables,     'ftemp',    float,  'ftemp',            '[DEBUG] ftemp'),
        #(variables,     'fvpd',     float,  'fVPD',             '[DEBUG] fVPD'),
        #(variables,     'fswp',     float,  'fSWP',             '[DEBUG] fSWP'),
        #(inputs,        'sinb',     float,  'sinB',             '[DEBUG] sinB'),
        #(variables,     'ppardir',  float,  'pPARdir',          '[DEBUG] pPARdir'),
        #(variables,     'ppardif',  float,  'pPARdiff',         '[DEBUG] pPARdiff'),
        #(variables,     'fpardir',  float,  'fPARdir',          '[DEBUG] fPARdir'),
        #(variables,     'fpardif',  float,  'fPARdiff',         '[DEBUG] fPARdiff'),
        #(variables,     'laisun',   float,  'LAIsun',           '[DEBUG] LAIsun'),
        #(variables,     'laishade', float,  'LAIshade',         '[DEBUG] LAIshade'),
        #(variables,     'parsun',   float,  'PARsun',           '[DEBUG] PARsun'),
        #(variables,     'parshade', float,  'PARshade',         '[DEBUG] PARshade'),
        #(variables,     'rsto_pet', float,  'Rsto_PEt (s/m)',       '[DEBUG] Rsto_PEt (Rsto_PEt, s/m)'),
        #(variables,     'gsto_pet', float,  'Gsto_PEt (mmol/m^2/s)','[DEBUG] Gsto_PEt (Gsto_PEt, mmol/m^2/s)'),
        #(variables,     'rb_h2o',   float,  'Rb_H2O (s/m)',     '[DEBUG] Rb_H2O (boundary resistance to water)'),
        #(variables,     'fpaw',     float,  'fPAW',             '[DEBUG] fPAW'),
        #(variables,     'fo3',      float,  'fO3',              '[DEBUG] fO3'),
)), 'variable', OrderedDict)

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
    ('fixedday', switchboard.leaf_fphen_fixed_day,      'Fixed day'),
    ('input',   switchboard.leaf_fphen_use_input,       'Use input'),
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

# SGS/EGS calculations (latitude function or inputs)
SGS_EGS_calcs = dicts_to_map(to_dicts(('id', 'func', 'name'), (
    ('inputs',      switchboard.sgs_egs_use_inputs,     'Use inputs below'),
    ('latitude',    switchboard.sgs_egs_latitude,       'Latitude function (forests)'),
)), 'id', OrderedDict)

default_SGS_EGS_calc = 'inputs'

#: Parameter definitions
paramdefs = dicts_to_map(to_dicts(('group', 'variable', 'cls', 'args', 'name', 'contexthelp'), (
    ('input', 'input_fields', None, None, 'Input data fields', ''),
    ('input', 'input_trim', None, None, 'Number of input rows to discard', ''),

    ('siteloc', 'lat', FloatSpinField, (-90, 90, 50, 0.1, 3), 'Latitude (decimal degrees North)', ''),
    ('siteloc', 'lon', FloatSpinField, (-180, 180, 0, 0.1, 3), 'Longitude (decimal degrees East)', ''),
    ('siteloc', 'elev', SpinField, (-100, 5000, 0), 'Elevation (m.a.s.l.)', ''),
    ('siteloc', 'soil_tex', ChoiceField, (soil_classes, default_soil_class), 'Soil texture', ''),
    ('siteloc', 'rsoil', SpinField, (1, 1000, 100), 'Rsoil (s/m)', ''),

    ('meas', 'o3zr', SpinField, (1, 200, 25), 'O3 measurement height (m)',
        'The height above ground level at which O3 concentration is measured'),
    ('meas', 'o3_h', disableable(FloatSpinField, 'Same as target canopy'), (0.1, 100, 25, 0.1, 1),
        'O3 measurement canopy height (m)',
        'The height of the vegetation that O3 concentration is measured above'),
    ('meas', 'uzr', SpinField, (1, 200, 25), 'Wind speed measurement height (m)',
        'The height above ground level at which windspeed is measured'),
    ('meas', 'u_h', disableable(FloatSpinField, 'Same as target canopy'), (0.1, 100, 25, 0.1, 1),
        'Wind speed measurement canopy height (m)',
        'The height of the vegetation over which windspeed is measured'),
    ('meas', 'd_meas', FloatSpinField, (0.1, 2, 0.5, 0.1, 1), 'Soil water measurement depth (m)', ''),

    ('vegchar', 'h', FloatSpinField, (0.1, 100, 25, 0.1, 1), 'Canopy height (h, m)', ''),
    ('vegchar', 'root', FloatSpinField, (0.1, 10, 1.2, 0.1, 1), 'Root depth (root, m)', ''),
    ('vegchar', 'lm', FloatSpinField, (0.01, 1, 0.05, 0.01, 2), 'Leaf dimension (Lm, m)', ''),
    ('vegchar', 'albedo', FloatSpinField, (0.01, 0.99, 0.12, 0.01, 2), 'Albedo (fraction)', ''),
    ('vegchar', 'gmax', SpinField, (1, 10000, 148), u'gmax (mmol O3/m\u00b2 PLA/s)', ''),
    ('vegchar', 'gmorph', FloatSpinField, (0.01, 1, 1, 0.01, 2), 'Sun/shade factor (fraction)', ''),
    ('vegchar', 'fmin', FloatSpinField, (0.01, 0.99, 0.13, 0.01, 2), 'fmin (fraction)', ''),
    ('vegchar', 'rext', SpinField, (0, 20000, 2500), 'External plant cuticle resistance (Rext, s/m)', ''),
    ('vegchar', 'y', FloatSpinField, (0.1, 100, 1.6, 0.1, 1), u'Threshold Y for PODy (nmol/m\u00b2/s)', ''),

    ('vegenv', 'f_lightfac', FloatSpinField, (0.001, 0.999, 0.006, 0.001, 3), 'light_a', ''),
    ('vegenv', 't_min', SpinField, (-10, 100, 0), u'Minimum temperature (T_min, \u00b0C)', ''),
    ('vegenv', 't_opt', SpinField, (-10, 100, 21), u'Optimum temperature (T_opt, \u00b0C)', ''),
    ('vegenv', 't_max', SpinField, (-10, 100, 35), u'Maximum temperature (T_max, \u00b0C)', ''),
    ('vegenv', 'vpd_max', FloatSpinField, (0, 100, 1, 0.01, 2), 'VPD for max. g (VPD_max, kPa)', ''),
    ('vegenv', 'vpd_min', FloatSpinField, (0, 100, 3.25, 0.01, 2), 'VPD for min. g (VPD_min, kPa)', ''),
    ('vegenv', 'vpd_crit', FloatSpinField, (0, 1000, 1000, 1, 1), 'Critical daily VPD sum (VPD_crit, kPa)', ''),
    ('vegenv', 'swp_min', FloatSpinField, (-6, 0, -1.25, 0.01, 2), 'SWP for min. g (SWP_min, MPa)', ''),
    ('vegenv', 'swp_max', FloatSpinField, (-6, 0, -0.05, 0.01, 2), 'SWP for max. g (SWP_max, MPa)', ''),

    ('modelopts', 'fo3', ChoiceField, (fO3_calcs, default_fO3_calc), 'fO3 calculation', ''),
    ('modelopts', 'fxwp', ChoiceField, (fXWP_calcs, default_fXWP_calc), 'Soil water influence on Gsto', ''),
    ('modelopts', 'lwp', ChoiceField, (LWP_calcs, default_LWP_calc), 'LWP calculation', ''),
    ('modelopts', 'fswp', ChoiceField, (fSWP_calcs, default_fSWP_calc), 'fSWP calculation', ''),

    ('season', 'sgs_egs_calc', ChoiceField, (SGS_EGS_calcs, default_SGS_EGS_calc), 'SGS/EGS method', ''),
    ('season', 'sgs', SpinField, (1, 365, 121), 'Start of growing season (SGS, day of year)', ''),
    ('season', 'egs', SpinField, (1, 365, 273), 'End of growing season (EGS, day of year)', ''),
    ('season', 'lai_a', FloatSpinField, (0, 20, 0, 0.1, 1), u'LAI at SGS (LAI_a, m\u00b2/m\u00b2)', ''),
    ('season', 'lai_b', FloatSpinField, (0, 20, 4, 0.1, 1), u'First mid-season LAI (LAI_b, m\u00b2/m\u00b2)', ''),
    ('season', 'lai_c', FloatSpinField, (0, 20, 4, 0.1, 1), u'Second mid-season LAI (LAI_c, m\u00b2/m\u00b2)', ''),
    ('season', 'lai_d', FloatSpinField, (0, 20, 0, 0.1, 1), u'LAI at EGS (LAI_d, m\u00b2/m\u00b2)', ''),
    ('season', 'lai_1', SpinField, (1, 250, 30), 'Period from LAI_a to LAI_b (LAI_1, days)', ''),
    ('season', 'lai_2', SpinField, (1, 250, 30), 'Period from LAI_c to LAI_d (LAI_2, days)', ''),
    ('season', 'sai', ChoiceField, (SAI_calcs, default_SAI_calc), 'SAI calculation', ''),

    ('fphen', 'fphen_a', FloatSpinField, (0, 1, 0, 0.1, 1), 'Fphen at SGS (fphen_a)', ''),
    ('fphen', 'fphen_b', FloatSpinField, (0, 1, 1, 0.1, 1), 'First mid-season Fphen (fphen_b)', ''),
    ('fphen', 'fphen_c', FloatSpinField, (0, 1, 1, 0.1, 1), 'Second mid-season Fphen (fphen_c)', ''),
    ('fphen', 'fphen_d', FloatSpinField, (0, 1, 1, 0.1, 1), 'Third mid-season Fphen (fphen_d)', ''),
    ('fphen', 'fphen_e', FloatSpinField, (0, 1, 0, 0.1, 1), 'Fphen at EGS (fphen_e)', ''),
    ('fphen', 'fphen_1', SpinField, (0, 200, 15), 'Period from fphen_a to fphen_b (fphen_1, days)', ''),
    ('fphen', 'fphen_lima', SpinField, (0, 365, 0), 'Start of SWP limitation (fphen_limA, day of year)', ''),
    ('fphen', 'fphen_2', SpinField, (0, 200, 1), 'Period from fphen_b to fphen_c (fphen_2, days)', ''),
    ('fphen', 'fphen_3', SpinField, (0, 200, 1), 'Period from fphen_c to fphen_d (fphen_3, days)', ''),
    ('fphen', 'fphen_limb', SpinField, (0, 365, 0), 'End of SWP limitation (fphen_limB, day of year)', ''),
    ('fphen', 'fphen_4', SpinField, (0, 200, 20), 'Period from fphen_d to fphen_e (fphen_4, days)', ''),

    ('leaf_fphen', 'leaf_fphen', ChoiceField, (leaf_fphen_calcs, default_leaf_fphen_calc), 'Leaf fphen calculation', ''),
    ('leaf_fphen', 'astart', SpinField, (1, 365, 153), 'Start of O3 accumulation (Astart, day of year)', ''),
    ('leaf_fphen', 'aend', SpinField, (1, 365, 208), 'End of O3 accumulation (Aend, day of year)', ''),
    ('leaf_fphen', 'leaf_fphen_a', FloatSpinField, (0, 1, 0, 0.1, 1), 'Leaf fphen at Astart (leaf_fphen_a)', ''),
    ('leaf_fphen', 'leaf_fphen_b', FloatSpinField, (0, 1, 1, 0.1, 1), 'Leaf fphen mid-season (leaf_fphen_b)', ''),
    ('leaf_fphen', 'leaf_fphen_c', FloatSpinField, (0, 1, 0, 0.1, 1), 'Leaf fphen at Aend (leaf_fphen_c)', ''),
    ('leaf_fphen', 'leaf_fphen_1', SpinField, (0, 300, 15), 'Period from leaf_fphen_a to leaf_fphen_b (days)', ''),
    ('leaf_fphen', 'leaf_fphen_2', SpinField, (0, 300, 30), 'Period from leaf_fphen_b to leaf_fphen_c (days)', ''),
)), 'variable', OrderedDict)


def parameters_by_group(group):
    """Get a list of all parameter definitions from :data:`parameters` that are in in *group*."""
    return [p for p in paramdefs.itervalues() if p['group'] == group]


def extract_outputs():
    """Extract all output variables.

    Extract a dict containing the values of all of the variables defined in
    output_fields.
    """
    return dict((x['variable'], x['type'](getattr(x['module'], x['variable']))) for x in output_fields.itervalues())
