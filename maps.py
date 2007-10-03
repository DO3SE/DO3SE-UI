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
    return [input_fields_rmap[x] for x in fields]

def InputFieldsToLong(fields):
    return [input_fields_map[x] for x in fields]
