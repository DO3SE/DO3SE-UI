module Switchboard

    integer, public, parameter :: sai_equals_lai = 1
    integer, public, parameter :: sai_forest     = 2
    integer, public, parameter :: sai_wheat      = 3
    integer, public, save :: sai_method = sai_equals_lai
    public :: SB_Calc_SAI

    integer, public, parameter :: rn_use_input  = 1
    integer, public, parameter :: rn_calculate  = 2
    integer, public, save :: rn_method = rn_use_input
    public :: SB_Calc_Rn

    integer, public, parameter :: leaf_fphen_equals_fphen = 1
    integer, public, parameter :: leaf_fphen_fixed_day    = 2
    integer, public, parameter :: leaf_fphen_use_input    = 3
    integer, public, save :: leaf_fphen_method = leaf_fphen_equals_fphen
    public :: SB_Calc_leaf_fphen

    integer, public, parameter :: ra_simple         = 1
    integer, public, parameter :: ra_with_heat_flux = 2
    integer, public, save :: ra_method = ra_simple
    public :: SB_Calc_Ra

    integer, public, parameter :: gsto_multiplicative = 1
    integer, public, parameter :: gsto_photosynthetic = 2
    integer, public, save :: gsto_method = gsto_multiplicative
    public :: SB_Calc_Gsto

    integer, public, parameter :: fo3_disabled = 1
    integer, public, parameter :: fo3_wheat    = 2
    integer, public, parameter :: fo3_potato   = 3
    integer, public, save :: fo3_method = fo3_disabled
    public :: SB_Calc_fO3

    integer, public, parameter :: fswp_exponential = 1
    integer, public, parameter :: fswp_linear      = 2
    integer, public, save :: fswp_method = fswp_exponential
    public :: SB_Calc_fSWP

    integer, public, parameter :: lwp_non_steady_state = 1
    integer, public, parameter :: lwp_steady_state     = 2
    integer, public, save :: lwp_method = lwp_non_steady_state
    public :: SB_Calc_LWP

    integer, public, parameter :: fxwp_disabled = 1
    integer, public, parameter :: fxwp_use_fswp = 2
    integer, public, parameter :: fxwp_use_flwp = 3
    integer, public, parameter :: fxwp_use_fpaw = 4
    integer, public, save :: fxwp_method = fxwp_disabled
    public :: SB_Calc_fXWP
    public :: SB_Calc_Es_blocked

    ! Both R and PAR are inputs, do nothing
    integer, public, parameter :: r_par_use_inputs = 1
    ! Derived R from PAR
    integer, public, parameter :: r_par_derive_r   = 2
    ! Derive PAR from R
    integer, public, parameter :: r_par_derive_par = 3
    integer, public, save :: r_par_method = r_par_use_inputs
    public :: SB_Calc_R_PAR

    ! Use supplied SGS/EGS
    integer, public, parameter :: sgs_egs_use_inputs = 1
    ! Use latitude function to calculate SGS/EGS
    integer, public, parameter :: sgs_egs_latitude   = 2
    integer, public, save :: sgs_egs_method = sgs_egs_use_inputs
    public :: SB_Calc_SGS_EGS


contains

    subroutine SB_Calc_SAI()
        use Phenology, only: Calc_SAI_Wheat
        use Variables, only: SAI, LAI

        select case (sai_method)
        
        case (sai_equals_lai)
            SAI = LAI
        
        case (sai_forest)
            SAI = LAI + 1
        
        case (sai_wheat)
            call Calc_SAI_Wheat()
        
        end select
    end subroutine SB_Calc_SAI

    subroutine SB_Calc_Rn()
        use Inputs, only: Rn, Rn_W, Calc_Rn

        select case (rn_method)
        
        case (rn_use_input)
            Rn_W = Rn * 277.8
        
        case (rn_calculate)
            call Calc_Rn()  ! Also calculates Rn_W
        
        end select
    end subroutine SB_Calc_Rn

    subroutine SB_Calc_leaf_fphen()
        use Phenology, only: Calc_leaf_fphen_fixed_day
        use Inputs, only: leaf_fphen_input
        use Variables, only: fphen, leaf_fphen

        select case (leaf_fphen_method)
        
        case (leaf_fphen_equals_fphen)
            leaf_fphen = fphen
        
        case (leaf_fphen_fixed_day)
            call Calc_leaf_fphen_fixed_day()

        case (leaf_fphen_use_input)
            leaf_fphen = leaf_fphen_input
        
        end select
    end subroutine SB_Calc_leaf_fphen

    subroutine SB_Calc_Ra()
        use R, only: Calc_Ra_Simple, Calc_Ra_With_Heat_Flux

        select case (ra_method)

        case (ra_simple)
            call Calc_Ra_Simple()

        case (ra_with_heat_flux)
            call Calc_Ra_With_Heat_Flux()

        end select
    end subroutine SB_Calc_Ra

    subroutine SB_Calc_gsto()
        use R, only: Calc_Rsto
        use Pn_Gsto, only: Calc_Gsto_Pn

        !select case (gsto_method)

        !case (gsto_multiplicative)
            call Calc_Rsto()

        !case (gsto_photosynthetic)
            call Calc_Gsto_Pn()

        !end select
    end subroutine SB_Calc_Gsto

    subroutine SB_Calc_fO3()
        use O3, only: Calc_fO3_Wheat, Calc_fO3_Potato
        use Variables, only: fO3

        select case (fo3_method)

        case (fo3_disabled)
            fO3 = 1.0

        case (fo3_wheat)
            call Calc_fO3_Wheat()

        case (fo3_potato)
            call Calc_fO3_Potato()

        end select
    end subroutine SB_Calc_fO3

    subroutine SB_Calc_fSWP()
        use SoilWater

        select case (fswp_method)
        case (fswp_exponential)
            call Calc_fSWP_exponential()
        case (fswp_linear)
            call Calc_fSWP_linear()
        end select
    end subroutine SB_Calc_fSWP

    subroutine SB_Calc_LWP()
        use SoilWater

        select case (lwp_method)
        case (lwp_non_steady_state)
            call Calc_LWP()
        case (lwp_steady_state)
            call Calc_LWP_steady_state()
        end select
    end subroutine SB_Calc_LWP

    subroutine SB_Calc_fXWP()
        use Variables, only: fXWP, fSWP, fLWP, fPAW

        select case (fxwp_method)

        case (fxwp_disabled)
            fXWP = 1.0

        case (fxwp_use_fswp)
            fXWP = fSWP

        case (fxwp_use_flwp)
            fXWP = fLWP

        case (fxwp_use_fpaw)
            fXWP = fPAW

        end select
    end subroutine SB_Calc_fXWP

    ! Calculate if there should be no soil evaporation depending on
    ! the current fSWP method
    subroutine SB_Calc_Es_blocked()
        use Soilwater, only: ASW_FC, ASW_max
        use Parameters, only: SWP_max
        use Variables, only: Es_blocked, ASW, SWP

        if (fxwp_method == fxwp_use_fpaw) then
            Es_blocked = (ASW < (ASW_FC * (ASW_max / 100.0)))
        else
            Es_blocked = (SWP < SWP_max)
        end if
    end subroutine SB_Calc_Es_blocked

    subroutine SB_Calc_R_PAR()
        use Inputs, only: R, PAR

        select case (r_par_method)

        ! Do nothing if using input data for both
        !case (r_par_use_inputs)

        case (r_par_derive_r)
            R = PAR / (0.45 * 4.57)

        case (r_par_derive_par)
            PAR = R * (0.45 * 4.57)

        end select
    end subroutine SB_Calc_R_PAR

    subroutine SB_Calc_SGS_EGS()
        use Parameters, only: lat, SGS, EGS
        use Phenology, only: Latitude_SGS_EGS

        select case (sgs_egs_method)

        ! Use inputs, nothing to do
        !case (sgs_egs_use_inputs)
        
        case (sgs_egs_latitude)
            call Latitude_SGS_EGS(lat, SGS, EGS)

        end select
    end subroutine SB_Calc_SGS_EGS

end module Switchboard
