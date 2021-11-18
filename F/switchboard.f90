module Switchboard

    public :: SB_Calc_SAI
    public :: SB_Calc_Rn
    public :: SB_Calc_leaf_fphen
    public :: SB_Calc_Ra
    public :: SB_Calc_Tleaf
    public :: SB_Calc_Gsto
    public :: SB_Calc_fO3
    public :: SB_Calc_fSWP
    public :: SB_Calc_LWP
    public :: SB_Calc_fXWP
    public :: SB_Calc_Es_blocked
    public :: SB_Calc_R_PAR
    public :: SB_Calc_SGS_EGS
    public :: SB_Calc_ustar


contains

    subroutine SB_Calc_SAI()
        use Phenology, only: Calc_SAI_Wheat
        use Options, only: sai_method, sai_equals_lai, sai_forest, sai_wheat
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
        use Options, only: rn_method, rn_use_input, rn_calculate

        select case (rn_method)

        case (rn_use_input)
            Rn_W = Rn * 277.8

        case (rn_calculate)
            call Calc_Rn()  ! Also calculates Rn_W

        end select
    end subroutine SB_Calc_Rn

    subroutine SB_Calc_leaf_fphen()
        use Phenology, only: Calc_leaf_fphen_fixed_day, Calc_tt_leaf_fphen
        use Inputs, only: leaf_fphen_input
        use Variables, only: fphen, leaf_fphen
        use Options, only: leaf_fphen_method, leaf_fphen_equals_fphen, leaf_fphen_fixed_day,&
         leaf_fphen_use_input, leaf_fphen_thermal_time

        select case (leaf_fphen_method)

        case (leaf_fphen_equals_fphen)
            leaf_fphen = fphen

        case (leaf_fphen_fixed_day)
            call Calc_leaf_fphen_fixed_day()

        case (leaf_fphen_use_input)
            leaf_fphen = leaf_fphen_input

        case (leaf_fphen_thermal_time)
            call Calc_tt_leaf_fphen()

        end select
    end subroutine SB_Calc_leaf_fphen

    subroutine SB_Calc_Ra()
        use R, only: Calc_Ra_Simple, Calc_Ra_With_Heat_Flux
        use Options, only: ra_method, ra_simple, ra_with_heat_flux

        select case (ra_method)

        case (ra_simple)
            call Calc_Ra_Simple()

        case (ra_with_heat_flux)
            call Calc_Ra_With_Heat_Flux()

        end select
    end subroutine SB_Calc_Ra

    subroutine SB_Calc_Tleaf()
        use Inputs, only: Tleaf_Estimate_db => Tleaf_Estimate_db
        use Options, only: tleaf_method, tleaf_estimate

        select case (tleaf_method)

        !case (tleaf_use_input)
        ! do nothing

        case (tleaf_estimate)
            call Tleaf_Estimate_db()

        end select
    end subroutine SB_Calc_Tleaf

    subroutine SB_Calc_gsto()
        use Inputs, only: R_ => R, eact, P, Tleaf, Ts_C, uh
        use R, only: Calc_Gsto_Multiplicative
        use Pn_Gsto, only: Calc_Gsto_Pn, leaf_temp_de_Boeck, gsto_final, pngsto_l, &
                pngsto, pngsto_c, pngsto_PEt
        use Variables, only: Gsto_l, Gsto, Gsto_c, Gsto_PEt
        use Parameters, only: Lm, albedo
        use Options, only: gsto_method, tleaf_method, tleaf_use_input, tleaf_estimate, &
            gsto_photosynthetic, gsto_multiplicative

        real :: Tleaf_balance_threshold, Tleaf_adjustment_factor
        integer :: Tleaf_max_iterations
        integer :: i

        Tleaf_balance_threshold = 0.0010000000474974513
        Tleaf_adjustment_factor = 0.019999999552965164
        Tleaf_max_iterations = 50

        ! Calculate both, because currently they don't overlap
        call Calc_Gsto_Multiplicative()
        call Calc_Gsto_Pn()

        select case (gsto_method)

        case (gsto_multiplicative)
            call Calc_Gsto_Multiplicative()
            ! TODO: Remove this, only here for debug when comparing methods
            ! call Calc_Gsto_Pn()

            select case (tleaf_method)

                case (tleaf_use_input)
                call Calc_Gsto_Pn()

                case (tleaf_estimate)
                    Tleaf = Ts_C
                    call Calc_Gsto_Pn()
                    ! Copy Calc_Gsto_Pn() results to correct places
                    do i= 1, 5
                        Tleaf = leaf_temp_de_Boeck(R_, eact*1e3, Ts_C, Tleaf, P*1e3, &
                                 uh, gsto_final*1e-6, .true., Lm, albedo, 1.0, &
                                 Tleaf_balance_threshold, &
                                 Tleaf_adjustment_factor, &
                                 Tleaf_max_iterations)
                        Tleaf = Ts_C + 0.2 * (Tleaf - Ts_C)
                        call Calc_Gsto_Pn()
                    end do
            end select


        case (gsto_photosynthetic)
            select case (tleaf_method)

                case (tleaf_use_input)
                call Calc_Gsto_Pn()

                case (tleaf_estimate)



                    Tleaf = Ts_C
                    call Calc_Gsto_Pn()
                    ! Copy Calc_Gsto_Pn() results to correct places
                    do i= 1, 5
                        Tleaf = leaf_temp_de_Boeck(R_, eact*1e3, Ts_C, Tleaf, P*1e3, &
                                 uh, gsto_final*1e-6, .true., Lm, albedo, 1.0, &
                                 Tleaf_balance_threshold, &
                                 Tleaf_adjustment_factor, &
                                 Tleaf_max_iterations)
                        Tleaf = Ts_C + 0.2 * (Tleaf - Ts_C)
                        call Calc_Gsto_Pn()
                    end do
                    Gsto_l = pngsto_l
                    Gsto = pngsto
                    Gsto_c = pngsto_c
                    Gsto_PEt = pngsto_PEt
            end select
        end select
    end subroutine SB_Calc_Gsto

    subroutine SB_Calc_fO3()
        use O3, only: Calc_fO3_Wheat, Calc_fO3_Potato
        use Variables, only: fO3
        use Options, only: fo3_method, fo3_disabled, fo3_wheat, fo3_potato

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
        use Options, only: fswp_method, fswp_exponential, fswp_linear

        select case (fswp_method)
        case (fswp_exponential)
            call Calc_fSWP_exponential()
        case (fswp_linear)
            call Calc_fSWP_linear()
        end select
    end subroutine SB_Calc_fSWP

    subroutine SB_Calc_LWP()
        use SoilWater
        use Options, only: lwp_method, lwp_non_steady_state, lwp_steady_state

        select case (lwp_method)
        case (lwp_non_steady_state)
            call Calc_LWP()
        case (lwp_steady_state)
            call Calc_LWP_steady_state()
        end select
    end subroutine SB_Calc_LWP

    subroutine SB_Calc_fXWP()
        use Variables, only: fXWP, fSWP, fLWP, fPAW
        use Options, only: fxwp_method, fxwp_disabled, fxwp_use_fswp, fxwp_use_flwp, fxwp_use_fpaw

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
        use Options, only: fxwp_method, fxwp_use_fpaw

        if (fxwp_method == fxwp_use_fpaw) then
            Es_blocked = (ASW < (ASW_FC * (ASW_max / 100.0)))
        else
            Es_blocked = (SWP < SWP_max)
        end if
    end subroutine SB_Calc_Es_blocked


    subroutine SB_Calc_R_PAR()
        use Inputs, only: R, PAR
        use Environmental, only:Calc_PAR_from_cloudfrac, Calc_ST_from_PAR
        use Options, only: r_par_method, r_par_derive_r, r_par_derive_par, r_par_derive_cloudfrac


        select case (r_par_method)

        ! Do nothing if using input data for both
        !case (r_par_use_inputs)
            ! TODO: May need to still recalculate sun shade fracs

        case (r_par_derive_r)
            call Calc_ST_from_PAR()
            R = (PAR / 4.57) / 0.45

        case (r_par_derive_par)
            PAR = R * (0.45 * 4.57)
            call Calc_ST_from_PAR()
        case (r_par_derive_cloudfrac)
            call Calc_PAR_from_cloudfrac()
            R = (PAR / 4.57) / 0.45
        end select
    end subroutine SB_Calc_R_PAR

    subroutine SB_Calc_SGS_EGS()
        use Parameters, only: lat, elev, SGS, EGS
        use Phenology, only: Latitude_SGS_EGS
        use Options, only: sgs_egs_method, sgs_egs_latitude

        select case (sgs_egs_method)

        ! Use inputs, nothing to do
        !case (sgs_egs_use_inputs)

        case (sgs_egs_latitude)
            call Latitude_SGS_EGS(lat, elev, SGS, EGS)

        end select
    end subroutine SB_Calc_SGS_EGS

    subroutine SB_Calc_ustar()
        use Inputs, only: Calc_ustar_uh, Calc_ustar_uh_ustar_in, Calc_ustar_uh_ustar_i_in
        use Options, only: ustar_method, ustar_calculate, ustar_input, ustar_i_input

        select case (ustar_method)

        case (ustar_calculate)
            call Calc_ustar_uh()
        case (ustar_input)
            call Calc_ustar_uh_ustar_in()
        case (ustar_i_input)
            call Calc_ustar_uh_ustar_i_in()

        end select

    end subroutine

end module Switchboard
