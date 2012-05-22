module Inputs

    use Functions
    use do3se_met

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

    subroutine Calc_sinB()
        use Parameters, only: lat, lon
        sinB = do3se_sinB(lat, lon, dd, hr)
    end subroutine Calc_sinB

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

    subroutine Tleaf_Estimate_Jackson()
        use Variables, only: Ra, Rsto_c

        Tleaf = do3se_leaf_temperature(Ts_C, P*1000, VPD*1000, esat*1000, eact*1000, Rn_W, Ra, Rsto_c)
    end subroutine Tleaf_Estimate_Jackson

    ! Calculated saturation/actual vapour pressure and relative humidity
    subroutine Calc_humidity()
        call do3se_humidity_from_VPD(Ts_C, VPD, esat, eact, RH)
    end subroutine Calc_humidity

end module Inputs
