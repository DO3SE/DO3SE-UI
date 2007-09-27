module Inputs

    real, public, save :: yr            ! Year
    real, public, save :: mm            ! Month
    real, public, save :: mdd           ! Day of Month
    real, public, save :: dd            ! Day of Year
    real, public, save :: hr            ! Hour
    real, public, save :: Ts_C          ! Surface air temperature (degrees C)
    real, public, save :: VPD           ! Vapour pressure deficit (kPa)
    real, public, save :: uh_zR          ! Wind speed at measurement height uzR (m/s)
    real, public, save :: precip        ! Precipitation (mm)
    real, public, save :: P             ! Atmospheric pressure (kPa)
    real, public, save :: O3_ppb_zR     ! O3 concentration at height czR (parts per billion)
    real, public, save :: Hd            ! Sensible heat flux (W/m^2)
    real, public, save :: R             ! Global radiation (Wh/m^2)
    real, public, save :: PAR           ! PAR (umol/m^2/s)

    ! These input variables usually aren't available, but have derivations
    real, public, save :: Rn            ! Net radiation (Wh/m^2)
    real, public, save :: ustar         ! Friction velocity (m/s)
    real, public, save :: uh_i          ! Windspeed at intermediate height
    real, public, save :: uh            ! Windspeed at canopy

    public :: Derive_PAR, Derive_R, Derive_ustar, Derive_ustar_uh

    contains

    !==========================================================================
    ! Derive the PAR radiation from the Global radiation input
    !==========================================================================
    subroutine Derive_PAR()
        PAR = R * (0.45 * 4.57)
    end subroutine Derive_PAR

    !==========================================================================
    ! Derive the Global radiation from the PAR input
    !==========================================================================
    subroutine Derive_R()
        R = PAR / (0.45 * 4.57)
    end subroutine Derive_R


    !==========================================================================
    ! Derive ustar for the flux canopy and the windspeed at that canopy
    !==========================================================================
    subroutine Derive_ustar_uh()
        use Constants, only: k, izR
        use Params_Site, only: u_d, u_h, u_zo, uzR
        use Params_Veg, only: h, d, zo

        real :: ustar_w     ! ustar for where windspeed is measured

        ! TODO: simplify some of the 'k' instances out
        !if (u_h /= h) then
            ! If the vegetation is different where the windspeed is measured 
            ! then calculate the values taking into account the differences
            ustar_w = (uh_zR * k) / log((uzR - u_d) / u_zo)
            uh_i = uh_zR + (ustar_w / k) * log((izR - u_d)/(uzR - u_d))
            ustar = (uh_i * k) / log((izR - d) / zo)
            uh = uh_i + (ustar / k) * log((h - d) / (izR - d))
        !else
            ! If there is no difference in vegetation, use a simpler 
            ! calculation
        !    ustar = (uh_zR * k) / log((uzR - d) / zo)
        !    uh = uh_zR + (ustar / k) * log((h - d) / (uzR - d))
        !end if

        ! Stop values from being 0
        ustar = max(0.0001, ustar)
        uh = max(0.0001, uh)
    end subroutine Derive_ustar_uh

    !==========================================================================
    ! Derive u* (ustar) instead of using an input (unused)
    ! TODO: remove me
    !==========================================================================
    subroutine Derive_ustar()
        use Constants, only: k
        use Params_Site, only: uzR, u_d, u_zo

        ! Uses max(...) to stop ustar from ever being 0
        ustar = (max(0.001, uh_zR) * k) / log((uzR - u_d) / u_zo)
    end subroutine Derive_ustar

    !==========================================================================
    ! The derivation for net radiation (Rn) is in the 'Irradiance' module 
    ! because it depends on other parts of that module.  Calc_Rn() derives Rn, 
    ! whereas Calc_Rn_Copy_From_Input() copies the Rn from the input value to
    ! the global Rn variable.
    !==========================================================================

end module Inputs
