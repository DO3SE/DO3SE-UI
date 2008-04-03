class Map:
    def __init__(self, mapping):
        self._mapping = mapping
        self._from = [a for a,b in mapping]
        self._to = [b for a,b in mapping]
        self._map = dict(mapping)
        self._rmap = dict([(b,a) for a,b in mapping])

    def __len__(self):
        return len(self._mapping)

    def map(self, x):
        return [self._map[i] for i in x]

    def rmap(self, x):
        return [self._rmap[i] for i in x]

    def keys(self):
        return self._from

    def values(self):
        return self._to

    def __iter__(self):
        return self._from.__iter__()

inputs = Map([
        ('yr',          'Year'),
        ('mm',          'Month'),
        ('mdd',         'Day of Month'),
        ('dd',          'Day of Year'),
        ('hr',          'Hour'),
        ('ts_c',        'Temperature (Celcius)'),
        ('vpd',         'Vapour Pressure Deficit (Pa)'),
        ('uh_zr',       'Wind speed (m/s)'),
        ('precip',      'Precipitation (mm)'),
        ('p',           'Pressure (kPa)'),
        ('o3_ppb_zr',   'O3 density (parts per billion)'),
        ('hd',          'Sensible heat flux (W/m^2)'),
        ('r',           'Global radiation (Wh/m^2)'),
        ('par',         'PAR radiation (umol/m^2/s)'),
        ('rn',          'Net radiation (Wh/m^2)'),
        ('ustar',       'Friction velocity (m/s)'),
])

outputs = Map([
        ('yr',          'Year'),
        ('mm',          'Month'),
        ('mdd',         'Day of Month'),
        ('dd',          'Day of Year'),
        ('hr',          'Hour'),
        ('ts_c',        'Temperature (Celcius)'),
        ('vpd',         'Vapour Pressure Deficit (Pa)'),
        ('uh_zr',       'Wind speed (m/s)'),
        ('precip',      'Precipitation (mm)'),
        ('p',           'Pressure (kPa)'),
        ('o3_ppb_zr',   'Measured O3 density (ppb)'),
        ('hd',          'Sensible heat flux (W/m^2)'),
        ('r',           'Global radiation (Wh/m^2)'),
        ('par',         'PAR radiation (umol/m^2/s)'),
        ('ustar',       'Friction velocity (m/s)'),
        ('rn',          'Net radiation (Rn, Wh/m^2)'),
        ('ra',          'Aerodynamic resistance (Ra, s/m)'),
        ('rb',          'Boundary layer resistance (Rb, s/m)'),
        ('rsur',        'Surface resistance (Rsur, s/m)'),
        ('rinc',        'In-canopy resistance (Rinc, s/m)'),
        ('rsto',        'Stomatal resistance (Rsto, s/m)'),
        ('gsto',        'Stomatal conductance (Gsto, m/s)'),
        ('rgs',         'Non-vegetative surface resistance (Rgs, s/m)'),
        ('vd',          'Deposition velocity (Vd, m/s)'),
        ('o3_ppb',      'Ozone concentration at canopy (O3_ppb, ppb)'),
        ('o3_nmol_m3',  'Ozone concentration at canopy (O3_nmol_m3, nmol/m^3)'),
        ('fst',         'Upper leaf stomatal O3 flux (Fst, nmol/m^2/s)'),
        ('afsty',       'Accumunlated Fst over threshold (AFstY, nmol/m^2/s)'),
        ('ftot',        'Total ozone flux (Ftot, nmol/m^2/s)'),
        ('ot40',        'Ozone over 40ppb (OT40, ppb)'),
        ('aot40',       'OT40 over growth period (AOT40, ppb)'),
        ('aet',         'Actual evapotranspiration (AEt, ???)'),
        ('swp',         'Soil-water potential (SWP, ???)'),
        ('per_vol',     'Volumetric water content (per_vol, %)'),
        ('smd',         'Soil moisture deficit (SMD, mm)'),
])

if __name__ == "__main__":
    for v in inputs:
        print v
