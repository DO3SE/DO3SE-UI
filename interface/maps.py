input_fields = {
        'yr'        : 'Year',
        'mm'        : 'Month',
        'mdd'       : 'Day of Month',
        'dd'        : 'Day of Year',
        'hr'        : 'Hour',
        'ts_c'      : 'Temperature (Celcius)',
        'vpd'       : 'Vapour Pressure Deficit (Pa)',
        'precip'    : 'Precipitation (mm)',
        'uh'        : 'Wind speed (m/s)',
        'o3_ppb_zr' : 'O3 density (parts per billion)',
        'idrctt'    : 'Direct radiation',
        'idfuse'    : 'Diffuse radiation',
        'zen'       : 'Zenith angle',
        }

input_fields_reverse = dict([(v, k) for k, v in input_fields.items()])

def InputFieldsToShort(fields):
    return [input_fields_reverse[x] for x in fields]

def InputFieldsToLong(fields):
    return [input_fields[x] for x in fields]
