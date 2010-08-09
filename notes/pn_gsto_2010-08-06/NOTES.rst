Hourly inputs are:
  + Photosynthetically Active Radiation (PAR) - already a model input
  + Windspeed at leaf surface - already an input
  + Air temperature - already an input
  + Relative humidity
      + Can be calculated from air temp, VPD and pressure
      + Don't bother allowing this as an input?
  + CO2 concentration
      + No sensible derivation
      + To simplify matters, set it as a per-site/per-dataset constant, example values in 
        documentation/tooltips
      + Default to mean atmospheric CO2 concentration from literature?
  + Leaf temperature
      + No sensible derivation?
      + Possibly use a simple derivation (e.g. = air temp) in absence of real data

Parameter inputs (vegetation-specific) are:

  + d: characteristic size of leaf (is this the same as Lm?)
  + alpha: Efficiency of light energy conversion
  + g_0: Conductance with closed stomata
  + m: "Sensitivity factor of conductance to assimilation" (fudge factor)
  + Teta: shape of J~Q determining factor (curve modifier for PAR to rate of electron transport 
    conversion)
  + Activity of rubisco enzyme response V_cmax:
      + V_cmax_25: max activity at 25 degrees
      + H_a_vcmax: activation energy for V_cmax
      + H_d_vcmax: deactivation energy for V_cmax
      + S_V_vcmax: entropy term
  + Electron transport rate response J_max:
      + J_max_25: max transport at 25 degrees
      + H_a_jmax: activation energy for J_max
      + H_d_jmax: deactivation energy for J_max
      + S_V_jmax: entropy term

Should hopefully be able to reduce parameter inputs to remove Teta, H_a/H_d and S_V.

**NOTE:** This method is going to be computationally more expensive than others due to it's 
iterative nature.  Maybe the value search can be improved?
