module Inputs

    use Functions

    integer, public, save :: yr            ! Year
    integer, public, save :: mm            ! Month
    integer, public, save :: mdd           ! Day of Month
    integer, public, save :: dd            ! Day of Year
    integer, public, save :: hr            ! Hour
    real, public, save :: Ts_C          ! Surface air temperature (degrees C)
    real, public, save :: Tleaf         ! Leaf temperature (degrees C)
    real, public, save :: VPD           ! Vapour pressure deficit (kPa)
    real, public, save :: uh_zR         ! Wind speed at measurement height uzR (m/s)
    real, public, save :: precip        ! Precipitation (mm)
    real, public, save :: P             ! Atmospheric pressure (kPa)
    real, public, save :: O3_ppb_zR     ! O3 concentration at height czR (parts per billion)
    real, public, save :: CO2           ! Ambient CO2 concentration (ppm)
    real, public, save :: Hd            ! Sensible heat flux (W/m^2)
    real, public, save :: R             ! Global radiation (Wh/m^2)
    real, public, save :: PAR           ! PAR (umol/m^2/s)

    ! These input variables usually aren't available, but have derivations
    real, public, save :: Rn            ! Net radiation (MJ/m^2/h)
    real, public, save :: leaf_fphen_input

    ! These input variables are always calculated from others
    real, public, save :: sinB          ! Solar elevation angle
    real, public, save :: Rn_W          ! Net radiation (W/m^2)
    real, public, save :: ustar         ! Friction velocity (m/s)
    real, public, save :: uh_i          ! Windspeed at intermediate height
    real, public, save :: uh            ! Windspeed at canopy
    real, public, save :: precip_acc    ! Previous day's accumulated precip (m)
    real, public, save :: esat          ! Saturated vapour pressure (kPa)
    real, public, save :: eact          ! Actual vapour pressure (kPa)
    real, public, save :: RH            ! Relative humidity (fraction)

    public :: Init_Inputs
    public :: Calc_ustar_uh
    public :: Accumulate_precip
    public :: Calc_precip_acc
    public :: Calc_sinB
    public :: Calc_Rn
    public :: Calc_humidity

    public :: do3se_velocity_from_ustar
    public :: do3se_ustar_from_velocity

    ! These are intermediate variables not used outside of this module
    real, private :: precip_dd  ! Accumulated precip for today so far

contains

    !
    ! Initialise accumulated inputs
    !
    subroutine Init_Inputs()
        precip_dd = 0
        precip_acc = 0
    end subroutine Init_Inputs


    pure function do3se_velocity_from_ustar(ustar, z, z0) result (u)
        real, intent(in)    :: ustar    ! Friction velocity (m/s)
        real, intent(in)    :: z        ! Height above boundary, e.g. z - d (m)
        real, intent(in)    :: z0       ! Roughness length, height at which u=0 (m)
        real                :: u        ! Output: velocity (m/s)

        real, parameter :: K = 0.41     ! von Karman's constant

        u = (ustar / K) * log(z / z0)
    end function do3se_velocity_from_ustar


    pure function do3se_ustar_from_velocity(u, z, z0) result (ustar)
        real, intent(in)    :: u        ! Velocity at height above boundary (m/s)
        real, intent(in)    :: z        ! Height above boundary, e.g. z - d (m)
        real, intent(in)    :: z0       ! Roughness length, height at which u=0 (m)
        real                :: ustar    ! Output: friction velocity, ustar (m/s)

        real, parameter :: K = 0.41 ! von Karman's constant

        ustar = (u * K) / log(z / z0)
    end function do3se_ustar_from_velocity


    pure subroutine do3se_vegetation_d_and_z0(h, d, z0)
        real, intent(in)    :: h    ! Vegetation height (m)
        real, intent(out)   :: d    ! Displacement height (m)
        real, intent(out)   :: z0   ! Roughness length (m)

        d = 0.7 * h
        z0 = 0.1 * h
    end subroutine do3se_vegetation_d_and_z0


    pure subroutine do3se_windspeed_transfer(uh_zR, h, u_h, uzR, uh_i, uh, ustar)
        real, intent(in)    :: uh_zR    ! Windspeed at measurement location (m/s)
        real, intent(in)    :: h        ! Target canopy height (m)
        real, intent(in)    :: u_h      ! Windspeed measurement canopy height (m)
        real, intent(in)    :: uzR      ! Windspeed measurement height (m)
        real, intent(out)   :: uh_i     ! Output: windspeed at "decoupled" height (m/s)
        real, intent(out)   :: uh       ! Output: windspeed at top of target canopy (m/s)
        real, intent(out)   :: ustar    ! Output: friction velocity over target canopy (m/s)

        real, parameter :: izR = 50     ! "Decoupled" height
        real, parameter :: MIN_WINDSPEED = 0.1
        real, parameter :: MIN_USTAR = 0.0001

        real :: ustar_ref   ! Friction velocity over windspeed measurement canopy
        real :: d, z0, u_d, u_z0

        call do3se_vegetation_d_and_z0(h, d, z0)
        call do3se_vegetation_d_and_z0(u_h, u_d, u_z0)

        ! Find ustar over reference canopy
        ustar_ref = do3se_ustar_from_velocity(max(MIN_WINDSPEED, uh_zR), uzR - u_d, u_z0)
        ! Find windspeed at izR, over reference canopy
        uh_i = max(MIN_WINDSPEED, do3se_velocity_from_ustar(ustar_ref, izR - u_d, u_z0))
        ! Find ustar over target canopy, assuming that at izR windspeed will be
        ! equal over both vegetations
        ustar = do3se_ustar_from_velocity(max(MIN_WINDSPEED, uh_i), izR - d, z0)
        ! Find windspeed at top of target canopy
        uh = max(MIN_WINDSPEED, do3se_velocity_from_ustar(ustar, h - d, z0))
        ! Stop ustar being 0
        ustar = max(MIN_USTAR, ustar)
    end subroutine do3se_windspeed_transfer


    !
    ! Derive ustar for the flux canopy and the windspeed at the canopy
    !
    subroutine Calc_ustar_uh()
        use Parameters, only: h, u_h, uzR

        call do3se_windspeed_transfer(uh_zR, h, u_h, uzR, uh_i, uh, ustar)
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

    ! =======================================================================
    ! Calculate sin(B), where B is the solar elevation angle.  Values less
    ! than 0 (below the horizon) are returned as 0.
    ! =======================================================================
    pure function do3se_sinB(lat, lon, dd, hr) result (sinB)
        real, intent(in)    :: lat      ! Latitude
        real, intent(in)    :: lon      ! Longitude
        integer, intent(in) :: dd       ! Day of year (1--365)
        integer, intent(in) :: hr       ! Hour of day (0--23)
        real                :: sinB     ! Output: sin() of solar elevation angle

        real :: f, e, t0, LC, lonm, h, dec

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
        dec = deg2rad(-23.4 * cos(deg2rad(360 * ((dd + 10) / 365.0))))

        ! sin() of solar elevation angle, between 0 and 1
        sinB = sin(deg2rad(lat))*sin(dec) + cos(deg2rad(lat))*cos(dec)*cos(h)
        sinB = max(0.0, sinB)
    end function do3se_sinB

    subroutine Calc_sinB()
        use Parameters, only: lat, lon
        sinB = do3se_sinB(lat, lon, dd, hr)
    end subroutine Calc_sinB

    ! =======================================================================
    ! Calculate net radiation
    ! =======================================================================
    pure function do3se_net_radiation(lat, lon, elev, albedo, dd, hr, R, &
                                      Ts_C, VPD, sinB) result (Rn)
        real, intent(in)    :: lat      ! Latitude
        real, intent(in)    :: lon      ! Longitude
        real, intent(in)    :: elev     ! Elevation (m)
        real, intent(in)    :: albedo   ! Surface albedo (fraction)
        integer, intent(in) :: dd       ! Day of year
        integer, intent(in) :: hr       ! Hour of day (0-23)
        real, intent(in)    :: R        ! Global radiation (W m-2)
        real, intent(in)    :: Ts_C     ! Temperature (degrees C)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (kPa)
        real, intent(in)    :: sinB     ! sin(B), B = solar elevation angle
        real                :: Rn       ! Output: net radiation (MJ)

        real, parameter     :: Gsc = 0.082          ! Solar constant (MJ/m^2/min)
        real, parameter     :: SBC = 4.903e-9 / 24  ! Stephan Boltzman constant
        real, parameter     :: PI = 3.141592653589793238

        real :: R_MJ, Ts_K, esat, eact, lat_rad, lonm, f, e, LC, t0, h, h1, h2, &
                dec, dr, Re, pR, Rnl, Rns

        ! Only calculate net radiation if sun is above the horizon
        if (sinB > 0) then
            ! Unit conversions
            R_MJ = R * 0.0036
            Ts_K = Ts_C + 273.16

            ! Saturation and actual vapour pressure (kPa)
            esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
            eact = esat - VPD

            ! Latitude in radians
            lat_rad = deg2rad(lat)

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
            h1 = h - (PI/24)
            h2 = h + (PI/24)

            ! Declination (radians)
            dec = deg2rad(-23.4 * cos(deg2rad(360 * ((dd + 10) / 365.0))))

            dr = 1 + (0.033 * cos(((2 * PI) / 365) * dd))
            ! External radiation (with fix to stop div by zero)
            ! TODO: fix this to be less hackish
            Re = max(0.00000000001, &
                    ((12 * 60) / PI) * Gsc * dr &
                        * ((h2 - h1) * sin(lat_rad) * sin(dec) &
                            + cos(lat_rad) * cos(dec) * (sin(h2) - sin(h1))))
            !Re = max(0.0, ((12*60)/PI)*Gsc*dr*sinB)

            ! Calculate net longwave radiation
            pR = (0.75 + (2e-5 * elev)) * Re

            Rnl = max(0.0, (SBC*(Ts_K**4)) * (0.34-(0.14*sqrt(eact))) &
                           * ((1.35*(min(1.0, R_MJ/pR)))-0.35))
            Rns = (1 - albedo) * R_MJ

            Rn = max(0.0, Rns - Rnl)
        else
            Rn = 0
        end if
    end function do3se_net_radiation

    !
    ! Calculate net radiation
    !
    subroutine Calc_Rn()
        use Parameters, only: elev, lat, lon
        use Parameters, only: albedo

        Rn = do3se_net_radiation(lat, lon, elev, albedo, dd, hr, R, Ts_C, VPD, sinB)
        ! Convert Rn to W/m2
        Rn_W = Rn * 277.8
    end subroutine Calc_Rn

    ! =======================================================================
    ! Calculate leaf temperature
    !
    ! Based on: Jackson, R.D. (1982). "Canopy temperature and crop water stress."
    !           Advances in irrigation, vol. 1, pp.43-85.  Specifically p.66 eq.9.
    ! =======================================================================
    pure function do3se_leaf_temperature (Tair, P, VPD, esat, eact, Rn, ra, rc) result (Tleaf)
        real, intent(in)    :: Tair     ! Ambient temperature (degrees C)
        real, intent(in)    :: P        ! Air pressure (Pa)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (Pa)
        real, intent(in)    :: esat     ! Saturation vapour pressure (Pa)
        real, intent(in)    :: eact     ! Actual vapour pressure (Pa)
        real, intent(in)    :: Rn       ! Net radiation (W m-2)
        real, intent(in)    :: ra       ! Aerodynamic resistance (s m-1)
        real, intent(in)    :: rc       ! Canopy resistance (s m-1)
        real                :: Tleaf    ! Output: leaf temperature (degrees C)

        real, parameter :: c_p = 1010.0     ! Specific heat capacity of dry air at 
                                            !   standard pressure and 20C, J kg-1 C-1
        real, parameter :: MAX_TDIFF = 5.0  ! Maximum allowed temperature difference

        real :: Tvir, rho, delta, lambda, psychro, Tdiff_1, Tdiff

        ! Virtual temperature for density calcualation (K)
        Tvir = (Tair + 273.15) / (1 - (0.378 * (eact / P)))
        ! Density of air (kg m-3)
        rho = P / (287.058 * Tvir)
        ! Slope of saturation vapour pressure curve (Pa C-1)
        delta = (4098 * esat) / ((Tair + 237.3)**2)
        ! Latent heat vapourisation of water (J kg-1)
        lambda = (-0.0000614342*Tair**3 + 0.00158927*Tair**2 - 2.36418*Tair + 2500.79) * 1000
        ! Psychrometric parameter (Pa C-1)
        psychro = 1628.6 * P / lambda

        ! Leaf - air temperature difference (C)
        Tdiff_1 = psychro * (1 + (rc / ra))
        Tdiff = ((ra * Rn) / (rho * c_p)) * (Tdiff_1 / (delta + Tdiff_1)) - (VPD / (delta + Tdiff_1))
        ! Stop Tdiff being too large
        Tdiff = max(-MAX_TDIFF, min(MAX_TDIFF, Tdiff))
        ! Leaf temperature (C)
        Tleaf = Tair + Tdiff
    end function do3se_leaf_temperature

    subroutine Tleaf_Estimate_Jackson()
        use Variables, only: Ra, Rsto_c

        Tleaf = do3se_leaf_temperature(Ts_C, P*1000, VPD*1000, esat*1000, eact*1000, Rn_W, Ra, Rsto_c)
    end subroutine Tleaf_Estimate_Jackson

    pure subroutine do3se_humidity_from_VPD(Ts_C, VPD, esat, eact, RH)
        real, intent(in)    :: Ts_C     ! Ambient temperature (degrees C)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (kPa)
        real, intent(out)   :: esat     ! Output: Saturation vapour pressure (kPa)
        real, intent(out)   :: eact     ! Output: Actual vapour pressure (kPa)
        real, intent(out)   :: RH       ! Output: Relative humidity (fraction)

        esat = 0.611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
        eact = esat - VPD
        RH = eact / esat
    end subroutine do3se_humidity_from_VPD

    pure subroutine do3se_VPD_from_humidity(Ts_C, RH, esat, eact, VPD)
        real, intent(in)    :: Ts_C     ! Ambient temperature (degrees C)
        real, intent(in)    :: RH       ! Relative humidity (fraction)
        real, intent(out)   :: esat     ! Output: Saturation vapour pressure (kPa)
        real, intent(out)   :: eact     ! Output: Actual vapour pressure (kPa)
        real, intent(out)   :: VPD      ! Output: Vapour pressure deficit (kPa)

        esat = 0.611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
        eact = esat * RH
        VPD = esat - eact
    end subroutine do3se_VPD_from_humidity

    ! Calculated saturation/actual vapour pressure and relative humidity
    subroutine Calc_humidity()
        call do3se_humidity_from_VPD(Ts_C, VPD, esat, eact, RH)
    end subroutine Calc_humidity

end module Inputs
