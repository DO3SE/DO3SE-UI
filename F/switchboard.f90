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
    integer, public, parameter :: leaf_fphen_wheat        = 2
    integer, public, parameter :: leaf_fphen_potato       = 3
    integer, public, save :: leaf_fphen_method = leaf_fphen_equals_fphen
    public :: SB_Calc_leaf_fphen

    integer, public, parameter :: ra_simple         = 1
    integer, public, parameter :: ra_with_heat_flux = 2
    integer, public, save :: ra_method = ra_simple
    public :: SB_Calc_Ra

    integer, public, parameter :: fo3_disabled = 1
    integer, public, parameter :: fo3_wheat    = 2
    integer, public, parameter :: fo3_potato   = 3
    integer, public, save :: fo3_method = fo3_disabled
    public :: SB_Calc_fO3

    integer, public, parameter :: fxwp_disabled = 1
    integer, public, parameter :: fxwp_use_fswp = 2
    !integer, public, parameter :: fxwp_use_flwp = 3
    integer, public, save :: fxwp_method = fxwp_disabled
    public :: SB_Calc_fXWP

    integer, public, parameter :: r_par_use_inputs = 1
    integer, public, parameter :: r_par_derive_r   = 2
    integer, public, parameter :: r_par_derive_par = 3
    integer, public, save :: r_par_method = r_par_use_inputs
    public :: SB_Calc_R_PAR

contains

    subroutine SB_Calc_SAI()
        use Phenology, only: Calc_SAI_copy_LAI, Calc_SAI_Forest, Calc_SAI_Wheat
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
        use Inputs, only: Rn_input => Rn
        use Variables, only: Rn, Rn_W
        use Irradiance, only: Calc_Rn

        select case (rn_method)
        
        case (rn_use_input)
            Rn = Rn_input
            Rn_W = Rn * 277.8
        
        case (rn_calculate)
            call Calc_Rn()
        
        end select
    end subroutine SB_Calc_Rn

    subroutine SB_Calc_leaf_fphen()
        use Phenology, only: Calc_leaf_fphen_Wheat
        use Variables, only: fphen, leaf_fphen

        select case (leaf_fphen_method)
        
        case (leaf_fphen_equals_fphen)
            leaf_fphen = fphen
        
        case (leaf_fphen_wheat)
            call Calc_leaf_fphen_Wheat()

        case (leaf_fphen_potato)
            ! Potato calculation is the same as that for wheat
            call Calc_leaf_fphen_Wheat()
        
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

    subroutine SB_Calc_fXWP()
        use Variables, only: fXWP, fSWP

        select case (fxwp_method)

        case (fxwp_disabled)
            fXWP = 1.0

        case (fxwp_use_fswp)
            fXWP = fSWP

        !case (fxwp_use_flwp)
        !    fXWP = fLWP

        end select
    end subroutine SB_Calc_fXWP

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

end module Switchboard
