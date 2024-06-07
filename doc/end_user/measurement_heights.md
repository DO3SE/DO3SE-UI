# Measurement Heights

There are various height parameters that can be set to determine the height at which measurements are taken. These are:


    ! Measurement heights
    real, public, save :: uzR = 25      ! Windspeed measurement height (m)
    real, public, save :: O3zR = 25     ! Ozone concentration measurement height (m)

    ! Properties of vegetation over which windspeed is measured (Must be less than measurement heights above)
    real, public, save :: u_h = 25      ! Canopy height (m)

    ! Properties of vegetation over which O3 concentration is measured  (Must be less than measurement heights above)
    real, public, save :: O3_h = 25     ! Canopy height (m)

    ! Properties of modelled canopy
    real, public, save :: h = 25            ! Canopy height (m)

We also have the constant izr which is the fully mixed height and is set at 45m