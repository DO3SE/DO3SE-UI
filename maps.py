input_fields = [
        'yr',
        'mm',
        'mdd',
        'dd',
        'hr',
        'ts_c',
        'vpd',
        'uh_zr',
        'precip',
        'p',
        'o3_ppb_zr',
        'hd',
        'r',
        'par',
        'rn',
        'ustar',
        ]

input_fields_long = [
        'Year',
        'Month',
        'Day of Month',
        'Day of Year',
        'Hour',
        'Temperature (Celcius)',
        'Vapour Pressure Deficit (Pa)',
        'Wind speed (m/s)',
        'Precipitation (mm)',
        'Pressure (kPa)',
        'O3 density (parts per billion)',
        'Sensible heat flux (W/m^2)',
        'Global radiation (Wh/m^2)',
        'PAR radiation (umol/m^2/s)',
        'Net radiation (Wh/m^2)',
        'Friction velocity (m/s)',
        ]

input_field_map = dict(zip(input_fields, input_fields_long))
input_field_rmap = dict(zip(input_fields_long, input_fields))

def InputFieldsToShort(fields):
    return [input_field_rmap[x] for x in fields]

def InputFieldsToLong(fields):
    return [input_field_map[x] for x in fields]

output_fields = [
        'rn',
        'ra',
        'rb',
        'rsur',
        'rinc',
        'rsto',
        'gsto',
        'rgs',
        'vd',
        'o3_ppb',
        'o3_nmol_m3',
        'fst',
        'afsty',
        'ftot',
        'ot40',
        'aot40',
        'aet',
        'swp',
        'per_vol',
        'smd', 
        ]

output_fields_long = [
        'Net radiation (Rn, Wh/m^2)',
        'Aerodynamic resistance (Ra, s/m)',
        'Boundary layer resistance (Rb, s/m)',
        'Surface resistance (Rsur, s/m)',
        'In-canopy resistance (Rinc, s/m)',
        'Stomatal resistance (Rsto, s/m)',
        'Stomatal conductance (Gsto, m/s)',
        'Non-vegetative surface resistance (Rgs, s/m)',
        'Deposition velocity (Vd, m/s)',
        'Ozone concentration at canopy (O3_ppb, ppb)',
        'Ozone concentration at canopy (O3_nmol_m3, nmol/m^3)',
        'Upper leaf stomatal O3 flux (Fst, nmol/m^2/s)',
        'Accumunlated Fst over threshold (AFstY, nmol/m^2/s)',
        'Total ozone flux (Ftot, nmol/m^2/s)',
        'Ozone over 40ppb (OT40, ppb)',
        'OT40 over growth period (AOT40, ppb)',
        'Actual evapotranspiration (AEt, ???)',
        'Soil-water potential (SWP, ???)',
        'Volumetric water content (per_vol, %)',
        'Soil moisture deficit (SMD, mm)',
        ]

output_field_map = dict(zip(output_fields, output_fields_long))
output_field_rmap = dict(zip(output_fields_long, output_fields))

def OutputFieldsToShort(fields):
    return [output_field_rmap[x] for x in fields]

def OutputFieldsToLong(fields):
    return [output_field_map[x] for x in fields]
