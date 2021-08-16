module Inputs

    real, public, save :: yr            ! Year
    real, public, save :: mm            ! Month
    real, public, save :: mdd           ! Day of Month
    real, public, save :: dd            ! Day of Year
    real, public, save :: td            ! thermal time
    real, public, save :: hr            ! Hour
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
    real, public, save :: cloudfrac     ! Fraction of cloud cover

    ! These input variables usually aren't available, but have derivations
    real, public, save :: Rn            ! Net radiation (MJ/m^2/h)
    real, public, save :: leaf_fphen_input

    ! These input variables are always calculated from others
    real, public, save :: sinB          ! Solar elevation angle
    real, public, save :: Rn_W          ! Net radiation (W/m^2)
    real, public, save :: ustar         ! Friction velocity (m/s)
    real, public, save :: uh_i          ! Windspeed at intermediate height
    real, public, save :: uh            ! Windspeed at canopy
    real, public, save :: L             ! Monin-Obukhov Length
    real, public, save :: invL          ! Inverse Monin-Obukhov Length
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

    public :: estimate_velocity
    public :: estimate_ustar
    public :: calc_monin_obukhov_length

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



    function calc_monin_obukhov_length(Tk, ustar, Hd, P) result(L)
        use Constants, only: Rmass, k, g, cp

        real, intent(in) :: Tk       ! Temperature in K
        real, intent(in) :: ustar    ! wind ustar
        real, intent(in) :: Hd       ! Grid Hd # Note should be +ve in middle of summer day
        real, intent(in) :: P        ! Grid Pressure kPa

        real :: rho, L, Hd_f

        Hd_f = Hd ! max(Hd, 0.000000000001) # Limit turned off to match EMEP
        ! Surface density of dry air (including conversion from to hPa to kPa)
        ! TODO: Check units
        rho = (P * 1000) / (Rmass * Tk)

        ! Monin-Obukhov Length
        L = -(Tk * ustar**3 * rho * cp) / (k * g * (-Hd_f))
        invL = 1/L ! should be -ve in middle of summer day


    end function


    !==========================================================================
    ! Estimate integral flux-gradient stability function for momentum
    !==========================================================================
    function calc_PsiM(zL) result (stab_m)
        use Constants, only: pi
        !   Out:
        !   PsiM = integral flux-gradient stability function for momentum
        !   Ref: Garratt, 1994, pp52-54

         real, intent(in) ::  zL    ! = surface layer stability parameter, (z-d)/L
                                    ! notation must be preserved
         real :: stab_m
         real  :: x

         if( zL < 0) then !unstable
            x    = sqrt(sqrt(1.0 - 16.0*zL))
            stab_m = log( 0.125*(1.0+x)*(1.0+x)*(1.0+x*x) ) +  PI/2.0 - 2.0*atan(x)
         else             !stable
             !ESX if ( FluxPROFILE == "Ln95" ) then
             !ESX    stab_m = -( a*zL + b*(zl-c/d)*exp(-d*zL) + b*c/d)
             !ESX else
                stab_m = -5.0 * zL
             !ESX end if
         end if

       end function calc_PsiM


    !==========================================================================
    ! Estimate Wind Velocity
    !==========================================================================
    ! function estimate_velocity(ustar, z, z0) result (u)
    !     use Constants, only: K
    !     real, intent(in) :: ustar   ! Friction velocity (m/s)
    !     real, intent(in) :: z       ! Height above boundary, e.g. z - d (m)
    !     real, intent(in) :: z0      ! Roughness length, height at which u=0 (m)

    !     real :: u                   ! Output: velocity (m/s)

    !     u = (ustar / K) * log(z / z0)
    ! end function estimate_velocity

    ! Updated to match EMEP
    function estimate_velocity(u_ref, z_ref, z, z0, d) result (u)
        real, intent(in) :: u_ref   ! velocity at izR (m/s)
        real, intent(in) :: z_ref   ! reference height (m)
        real, intent(in) :: z       ! Target height (m)
        real, intent(in) :: z0      ! Roughness length, height at which u=0 (m)
        real, intent(in) :: d       ! displacement height(m)

        real :: u, zr, zt                   ! Output: velocity (m/s)

        zt = z-d
        zr = z_ref - d

        u = u_ref * log(zt/z0)/log(zr/z0)

    end function estimate_velocity


    !==========================================================================
    ! Estimate Wind U*
    !==========================================================================
    function estimate_ustar(u, z, z0, L) result (ustar)
        use Constants, only: K
        real, intent(in) :: u       ! Velocity at height above boundary (m/s)
        real, intent(in) :: z       ! Height above boundary, e.g. z - d (m)
        real, intent(in) :: z0      ! Roughness length, height at which u=0 (m)

        real :: ustar, L, psim_a, psim_b               ! Output: friction velocity, ustar (m/s)

        psim_a = 1 ! calc_PsiM(z/L)
        psim_b = 1 ! calc_PsiM(z0/L)
        ustar = (u * K) / (log(z / z0) - psim_a + psim_b)
    end function estimate_ustar

    !==========================================================================
    ! Calc Monin-Obukhov Length for row
    !==========================================================================
    subroutine Calc_monin_obukhov_length_row()
        use Constants, only: Ts_K
        real ::  Tk
        Tk = Ts_C + Ts_K
        L = calc_monin_obukhov_length(Tk, ustar, Hd, P)
    end subroutine Calc_monin_obukhov_length_row

    !==========================================================================
    ! Derive ustar for the flux canopy and the windspeed at the canopy
    !==========================================================================
    subroutine Calc_ustar_uh()
        use Constants, only: Rmass, Ts_K, k, g, cp, pi, izR
        use Parameters, only: h, d, zo, u_d, u_zo, uzR

        real :: ustar_ref   ! ustar for where windspeed is measured
        real :: Tk
        real :: uh_zr_lim

        real, parameter :: MIN_WINDSPEED = 0.1

        Tk = Ts_C + Ts_K

        ! Find ustar over reference canopy
        uh_zr_lim = max(MIN_WINDSPEED, uh_zR)

        ! TODO: What is the diff between u_d and d and u_zo and zo?
        ustar_ref = estimate_ustar(uh_zr_lim, uzR - u_d, u_zo, L)
        ! Find windspeed at izR, over reference canopy
        uh_i = estimate_velocity(uh_zR_lim, uzR, izR, zo, d)
        uh_i = max(MIN_WINDSPEED, uh_i)
        ! Find ustar over target canopy, assuming that at izR windspeed will be
        ! equal over both vegetations
        ustar = estimate_ustar(uh_i, izR - d, zo, L)
        ! Find windspeed at top of target canopy
        uh = estimate_velocity(uh_i, izR, h, zo, d)
        uh = max(MIN_WINDSPEED, uh)

        ! Stop ustar being 0
        ustar = max(0.0001, ustar)
    end subroutine Calc_ustar_uh

    !==========================================================================
    ! Accumulate precipitation for the day, converted to metres
    !==========================================================================
    subroutine Accumulate_precip()
        precip_dd = precip_dd + (precip/1000)
    end subroutine Accumulate_precip

    !==========================================================================
    ! Store the previous day's accumulated precipitation
    !==========================================================================
    subroutine Calc_precip_acc()
        precip_acc = precip_dd
        precip_dd = 0
    end subroutine Calc_precip_acc

    !==========================================================================
    ! Calculate the solar elevation angle, using the geographical location of
    ! the site and the time of day and day of year.  Also calculates h and dec
    ! which are required for Rn calculation.
    !==========================================================================
    subroutine Calc_sinB()
        ! TODO: document variables
        use Parameters, only: lat, lon
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
        dec = deg2rad(-23.4 * cos(deg2rad(360 * ((dd + 10) / 365.0))))

        sinB = sin(deg2rad(lat))*sin(dec) + cos(deg2rad(lat))*cos(dec)*cos(h)
        sinB = max(0.0, sinB)
    end subroutine Calc_sinB

    !==========================================================================
    ! Calculate net radiation
    !==========================================================================
    subroutine Calc_Rn()
        ! TODO: document variables
        use Parameters, only: elev, lat
        use Parameters, only: albedo
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
            Ts_K = Ts_C + 273.15

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

    !==========================================================================
    ! Calculate leaf temperature
    !
    ! Based on: Jackson, R.D. (1982). "Canopy temperature and crop water stress."
    !           Advances in irrigation, vol. 1, pp.43-85.  Specifically p.66 eq.9.
    !==========================================================================
    real function Calc_Tleaf (Tair, P, VPD, Rn, ra, rc)
        implicit none

        real, intent(in) :: Tair    ! Ambient temperature (C)
        real, intent(in) :: P       ! Air pressure (Pa)
        real, intent(in) :: VPD     ! Vapour pressure deficit (Pa)
        real, intent(in) :: Rn      ! Net radiation (W m-2)
        real, intent(in) :: ra      ! Aerodynamic resistance (s m-1)
        real, intent(in) :: rc      ! Canopy resistance (s m-1)

        real, parameter :: c_p = 1010.0     ! Specific heat capacity of dry air at
                                            !   standard pressure and 20C, J kg-1 C-1
        real, parameter :: MAX_TDIFF = 5.0  ! Maximum allowed temperature difference

        real :: esat, eact, Tvir, rho, delta, lambda, psychro, Tdiff_1, Tdiff

        ! Saturation vapour pressure at Tair (Pa)
        esat = 611 * exp(17.27 * Tair / (Tair + 237.3))
        ! Actual vapour pressure (Pa)
        eact = esat - VPD
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
        Calc_Tleaf = Tair + Tdiff
    end function Calc_Tleaf

    !==========================================================================
    ! Tleaf estimate db
    !==========================================================================
    subroutine Tleaf_Estimate_db()
        ! use Variables, only: Ra, Rsto_c

        !Tleaf = Calc_Tleaf(Ts_C, P*1000, VPD*1000, Rn_W, Ra, Rsto_c)
    end subroutine Tleaf_Estimate_db

    !==========================================================================
    ! Calculated saturation/actual vapour pressure and relative humidity
    !==========================================================================
    subroutine Calc_humidity()
        esat = 0.611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
        eact = esat - VPD
        RH = eact / esat
    end subroutine Calc_humidity

end module Inputs
