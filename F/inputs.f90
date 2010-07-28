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
    real, public, save :: ustar         ! Friction velocity (m/s)
    real, public, save :: uh_i          ! Windspeed at intermediate height
    real, public, save :: uh            ! Windspeed at canopy

    public :: Calc_ustar_uh

    contains


    !==========================================================================
    ! Derive ustar for the flux canopy and the windspeed
    !
    !
    !==========================================================================
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

    !==========================================================================
    ! The derivation for net radiation (Rn) is in the 'Irradiance' module 
    ! because it depends on other parts of that module.  Calc_Rn() derives Rn, 
    ! whereas Calc_Rn_Copy_From_Input() copies the Rn from the input value to
    ! the global Rn variable.
    !==========================================================================

end module Inputs
