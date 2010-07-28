module Inputs

    real, public, save :: yr            ! Year
    real, public, save :: mm            ! Month
    real, public, save :: mdd           ! Day of Month
    real, public, save :: dd            ! Day of Year
    real, public, save :: hr            ! Hour
    real, public, save :: Ts_C          ! Surface air temperature (degrees C)
    real, public, save :: VPD           ! Vapour pressure deficit (kPa)
    real, public, save :: uh_zR         ! Wind speed at measurement height uzR (m/s)
    real, public, save :: precip        ! Precipitation (mm)
    real, public, save :: P             ! Atmospheric pressure (kPa)
    real, public, save :: O3_ppb_zR     ! O3 concentration at height czR (parts per billion)
    real, public, save :: Hd            ! Sensible heat flux (W/m^2)
    real, public, save :: R             ! Global radiation (Wh/m^2)
    real, public, save :: PAR           ! PAR (umol/m^2/s)

    ! These input variables usually aren't available, but have derivations
    real, public, save :: Rn            ! Net radiation (MJ/m^2/h)

    ! These input variables are always calculated from others
    real, public, save :: sinB          ! Solar elevation angle
    real, public, save :: Rn_W          ! Net radiation (W/m^2)
    real, public, save :: ustar         ! Friction velocity (m/s)
    real, public, save :: uh_i          ! Windspeed at intermediate height
    real, public, save :: uh            ! Windspeed at canopy
    real, public, save :: precip_acc    ! Previous day's accumulated precip (m)

    public :: Init_Inputs
    public :: Calc_ustar_uh
    public :: Accumulate_precip
    public :: Calc_precip_acc
    public :: Calc_sinB
    public :: Calc_Rn

    ! These are intermediate variables not used outside of this module
    real, private :: precip_dd  ! Accumulated precip for today so far
    real, private :: h          ! "Hour angle" of the sun
    real, private :: dec        ! Declination (radians)

contains

    !
    ! Initialise accumulated inputs
    !
    subroutine Init_Inputs()
        precip_dd = 0
        precip_acc = 0
    end subroutine Init_Inputs

    !
    ! Derive ustar for the flux canopy and the windspeed at the canopy
    !
    subroutine Calc_ustar_uh()
        use Constants, only: k, izR
        use Params_Site, only: u_d, u_zo, uzR
        use Params_Veg, only: h, d, zo

        real :: ustar_w     ! ustar for where windspeed is measured

        ustar_w = (uh_zR * k) / log((uzR - u_d) / u_zo)
        uh_i = uh_zR + (ustar_w / k) * log((izR - u_d)/(uzR - u_d))
        ustar = (uh_i * k) / log((izR - d) / zo)
        uh = uh_i + (ustar / k) * log((h - d) / (izR - d))

        ! Stop values from being 0
        ustar = max(0.0001, ustar)
        uh = max(0.0001, uh)
        uh_i = max(0.0001, uh_i)
    end subroutine Calc_ustar_uh

    !
    ! Accumulate precipitation for the day, converted to metres
    !
    subroutine Accumulate_precip()
        precip_dd = precip_dd + (precip/1000)
    end subroutine Accumulate_precip

    !
    ! Store the previous day's accumulated precipitation
    !
    subroutine Calc_precip_acc()
        precip_acc = precip_dd
        precip_dd = 0
    end subroutine Calc_precip_acc

    !
    ! Calculate the solar elevation angle, using the geographical location of 
    ! the site and the time of day and day of year.  Also calculates h and dec
    ! which are required for Rn calculation.
    !
    subroutine Calc_sinB()
        ! TODO: document variables
        use Params_Site, only: lat, lon
        use Functions, only: deg2rad, rad2deg

        real :: f, e, t0, LC, lonm

        ! Calculate the longitudinal meridian
        lonm = nint(lon / 15.0) * 15.0

        ! Solar noon correction for day of year
        f = deg2rad(279.575 + (0.9856 * dd))
        e = (-104.7*sin(f) + 596.2*sin(2*f) + 4.3*sin(3*f) - 12.7*sin(4*f) &
            - 429.3*cos(f) - 2.0*cos(2*f) + 19.3*cos(3*f)) / 3600

        ! Solar noon, with day of year and longitudinal correction
        LC = (lon - lonm) / 15
        t0 = 12 - LC - e

        ! Hour-angle of the sun
        h = deg2rad(15 * (hr - t0))

        ! Declination (radians)
        dec = deg2rad(-23.4 * cos(deg2rad(360 * ((dd + 10) / 365))))

        sinB = sin(deg2rad(lat))*sin(dec) + cos(deg2rad(lat))*cos(dec)*cos(h)
        sinB = max(0.0, sinB)
    end subroutine Calc_sinB

    !
    ! Calculate net radiation
    !
    subroutine Calc_Rn()
        ! TODO: document variables
        use Params_Site, only: elev, lat
        use Params_Veg, only: albedo
        use Constants, only: pi
        use Functions, only: deg2rad, rad2deg

        real :: R_MJ, Ts_K, dr, Re, pR, esat, eact, Rnl, Rns, lat_rad, h1, h2

        ! Constants
        real, parameter :: Gsc = 0.082            ! Solar constant (MJ/m^2/min)
        real, parameter :: SBC = 4.903e-9 / 24    ! Stephan Boltzman constant

        lat_rad = deg2rad(lat)

        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        eact = esat - VPD

        if (sinB > 0) then
            ! Unit conversions
            R_MJ = R * 0.0036
            Ts_K = Ts_C + 273.16

            ! Hour angle stuff
            h1 = h - (pi/24)
            h2 = h + (pi/24)

            dr = 1 + (0.033 * cos(((2 * pi) / 365) * dd))
            ! External radiation (with fix to stop div by zero)
            ! TODO: fix this to be less hackish
            Re = max(0.00000000001, &
                    ((12 * 60) / pi) * Gsc * dr &
                        * ((h2 - h1) * sin(lat_rad) * sin(dec) &
                            + cos(lat_rad) * cos(dec) * (sin(h2) - sin(h1))))
            !Re = max(0.0, ((12*60)/pi)*Gsc*dr*sinB)

            ! Calculate net longwave radiation
            pR = (0.75 + (2e-5 * elev)) * Re

            Rnl = max(0.0, (SBC*(Ts_K**4)) * (0.34-(0.14*sqrt(eact))) * ((1.35*(min(1.0, R_MJ/pR)))-0.35))
            Rns = (1 - albedo) * R_MJ

            Rn = max(0.0, Rns - Rnl)
        else
            Rn = 0
        end if

        ! Calculate Rn in W/m2
        Rn_W = Rn * 277.8
    end subroutine Calc_Rn

end module Inputs
