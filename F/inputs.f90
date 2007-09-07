module Inputs

    real, public, save :: yr            ! Year
    real, public, save :: mm            ! Month
    real, public, save :: mdd           ! Day of Month
    real, public, save :: dd            ! Day of Year
    real, public, save :: hr            ! Hour
    real, public, save :: Ts_C          ! Surface air temperature (degrees C)
    real, public, save :: VPD           ! Vapour pressure deficit (kPa)
    real, public, save :: u_uzR         ! Wind speed at measurement height uzR (m/s)
    real, public, save :: precip        ! Precipitation (mm)
    real, public, save :: P             ! Atmospheric pressure (kPa)
    real, public, save :: O3_ppb_czR    ! O3 concentration at height czR (parts per billion)
    real, public, save :: LAI           ! Leaf area index (m^2/m^2)
    real, public, save :: Hd            ! Sensible heat flux (W/m^2)
    real, public, save :: R             ! Global radiation (Wh/m^2)
    real, public, save :: PAR           ! PAR (umol/m^2/s)

    ! These input variables usually aren't available, but have derivations
    real, public, save :: Rn            ! Net radiation (Wh/m^2)
    real, public, save :: ustar         ! Friction velocity (m/s)

    public :: Derive_PAR, Derive_R, Derive_ustar

    contains

    !**************************************************************************
    ! Derive the PAR radiation from the Global radiation input
    !**************************************************************************
    subroutine Derive_PAR()
        PAR = R * (0.45 * 4.57)
    end subroutine Derive_PAR

    !**************************************************************************
    ! Derive the Global radiation from the PAR input
    !**************************************************************************
    subroutine Derive_R()
        R = PAR / (0.45 * 4.57)
    end subroutine Derive_R

    !**************************************************************************
    ! Derive u* (ustar) instead of using an input
    !**************************************************************************
    subroutine Derive_ustar()
        use Constants, only: k
        use Params_Site, only: uzR, u_d, u_zo

        ustar = (u_uzR * k) / log((uzR - u_d) / u_zo)
    end subroutine Derive_ustar

    !**************************************************************************
    ! The derivation for net radiation (Rn) is in the 'Irradiance' module 
    ! because it depends on other parts of that module.  Calc_Rn() derives Rn, 
    ! whereas Calc_Rn_Copy_From_Input() copies the Rn from the input value to
    ! the global Rn variable.
    !**************************************************************************

end module Inputs
