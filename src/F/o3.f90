module O3


    real, public, save :: ustar_ref_o3  ! ustar_ref for O3 calcs

    public :: Calc_O3_Concentration, Calc_Ftot
    public :: Calc_Fst, Calc_AFstY, Calc_AOT40
    public :: Calc_fO3_Ignore, Calc_fO3_Wheat, Calc_fO3_Potato

contains

    !==========================================================================
    ! Calculate the ozone concentration at the canopy
    !
    ! This procedure results in the calculation of deposition velocity (Vd) and
    ! the ozone concentration at the canopy in both parts-per-billion and
    ! nmol/m^3

    ! We translate the ozone from the measured height up to a decoupled height
    ! then back down to the target canopy. As the measured data may have had a canopy
    ! of a different height we need to calculate the deposition velocity for a
    ! reference canopy.
    !==========================================================================
    subroutine Calc_O3_Concentration()
        use Constants, only: k, izR, v, DO3, Pr, Ts_K
        use Inputs, only: O3_ppb_zR, uh_i, Ts_C, P, ustar, L, invL, ustar_ref_O3
        use Inputs, only: estimate_ustar,estimate_ustar_simple
        use Variables, only: Ra, Rb, Rsur, Rb_ref
        use Variables, only: Vd, O3_ppb, O3_nmol_m3, Vd_i, O3_ppb_i, Ra_ref_i, &
                             Ra_O3zR_i, Ra_tar_i
        use Parameters, only: O3zR, O3_d, O3_zo, d, zo
        use R, only: calc_ra_simple => ra_simple, calc_ra_with_heat_flux=>ra_heat_flux, rb_func => rb
        use Options, only: ra_method, ra_simple, ra_with_heat_flux


        real, parameter :: M_O3 = 48.0      ! Molecular weight of O3 (g)

        real ::  Vn

        ! Ra between reference canopy and izR
        select case (ra_method)
            case (ra_simple)
                Ra_ref_i = calc_ra_simple(ustar_ref_O3, O3_zo + O3_d, izR, O3_d)
            case (ra_with_heat_flux)
                Ra_ref_i = calc_ra_with_heat_flux(ustar_ref_O3, O3_zo + O3_d, izR, invL)
        end select
        ! Rb for reference canopy
        Rb_ref = rb_func(ustar_ref_o3, DO3)
        ! Deposition velocity at izR over reference canopy
        ! (assuming that Rsur_ref = Rsur)
        ! The deposition velocity between the measured height and decoupled height is
        ! effected by the canopy below the measured height not our modelled canopy!s
        Vd_i = 1.0 / (Ra_ref_i + Rb_ref + Rsur)
        ! Ra between measurement height and izR
        select case (ra_method)
            case (ra_simple)
                Ra_O3zR_i = calc_ra_simple(ustar_ref_o3, O3zR, izR, O3_d)
            case (ra_with_heat_flux)
                Ra_O3zR_i = calc_ra_with_heat_flux(ustar_ref_o3, O3zR, izR, invL)
        end select

        ! O3 concentration at izR
        O3_ppb_i = O3_ppb_zR / (1.0 - (Ra_O3zR_i * Vd_i))

        ! Ra between target canopy and izR
        ! Same as Ra from r.f90 but lower height includes +h*0.78 and upper height removes h*0.78
        ! (ustar already calculated for target canopy)
        ! NOTE: ustar is calculated for windspeed heights not O3 heights
        select case (ra_method)
            case (ra_simple)
                Ra_tar_i = calc_ra_simple(ustar, zo + d, izR, d)
            case (ra_with_heat_flux)
                Ra_tar_i = calc_ra_with_heat_flux(ustar, zo + d, izR, invL)
        end select

        ! Deposition velocity at izR over target canopy
        Vd = 1.0 / (Ra_tar_i + Rb + Rsur)
        ! O3 concentration at target canopy
        ! (Ra already calculated between canopy height and izR)
        O3_ppb = O3_ppb_i * (1.0 - (Ra * Vd))

        ! Specific molar volume of an ideal gas at current temp + pressure
        Vn = 8.314510 * ((Ts_C + Ts_K) / P)
        ! Convert to nmol/m^3
        O3_nmol_m3 = (1.0/Vn) * O3_ppb * M_O3 * 20.833  ! 1 microgram O3 = 20.833 nmol/m^3
    end subroutine Calc_O3_Concentration

    !==========================================================================
    ! Calculate the total ozone flux to the vegetated surface
    !==========================================================================
    subroutine Calc_Ftot()
        use Variables, only: Ftot, O3_nmol_m3, Vd

        Ftot = O3_nmol_m3 * Vd
    end subroutine Calc_Ftot

    !==========================================================================
    ! Calculate the upper leaf stomatal ozone flux
    !==========================================================================
    subroutine Calc_Fst()
        use Parameters, only: Lm, Rext
        use Inputs, only: uh
        use Variables, only: Gsto_l, Rsto_l, O3_nmol_m3, Fst, Fst_sun, Rsun_l

        real :: leaf_rb, leaf_r_l, leaf_rs


        if (Gsto_l > 0) then
            leaf_rb = 1.3 * 150 * sqrt(Lm/uh)   ! leaf boundary layer resistance (s/m)
            leaf_r_l = 1.0 / ((1.0/Rsto_l) + (1.0/Rext))  ! leaf resistance in s/m
            Fst = O3_nmol_m3 * (1/Rsto_l) * (leaf_r_l / (leaf_rb + leaf_r_l))

            leaf_rs = 1.0 / ((1.0/Rsto_l) + (1.0/Rext))  ! resistance in s/m
            Fst_sun = O3_nmol_m3 *(leaf_rs / (leaf_rb + leaf_rs)) *  (1/Rsun_l)
        else
            Fst = 0
            Fst_sun = 0
        end if
    end subroutine Calc_Fst

    !==========================================================================
    ! Calculate the accumulated stomatal flux above threshold Y
    !==========================================================================
    subroutine Calc_AFstY()
        use Variables, only: Fst, Fst_sun, AFstY, AFst0, AFstY_total
        use Parameters, only: Y

        ! Fst == 0 if Gsto_l == 0 (and Gsto_l == 0 if leaf_fphen == 0), so no
        ! need to check leaf_fphen
        AFst0 = AFst0 + ((Fst_sun*60*60)/1000000)
        AFstY = AFstY + ((max(0.0, Fst_sun - Y)*60*60)/1000000)
        AFstY_total = AFstY_total + ((max(0.0, Fst - Y)*60*60)/1000000)
    end subroutine Calc_AFstY


    !==========================================================================
    ! Calculate the accumulated OT40
    !==========================================================================
    subroutine Calc_AOT40()
        use Inputs, only: R
        use Variables, only: OT0, OT40, AOT0, AOT40, O3_ppb, fphen, leaf_fphen

        ! Default OT0 and OT40 to 0
        OT0 = 0
        OT40 = 0

        ! Only accumulate OT when global radiation > 50 W/m^2
        if (R > 50.0) then
            ! Only accumulate OT0 when leaf_fphen > 0
            if (leaf_fphen > 0) then
                OT0 = O3_ppb / 1000
            end if
            ! Only accumulate OT40 when fphen > 0
            if (fphen > 0) then
                OT40 = max(0.0, O3_ppb - 40) / 1000
            end if
        end if

        ! Accumulate
        AOT0 = AOT0 + OT0
        AOT40 = AOT40 + OT40
    end subroutine Calc_AOT40

    !==========================================================================
    ! Set fO3 to 1.0, so it is ignored by Gsto calculation
    !==========================================================================
    subroutine Calc_fO3_Ignore()
        use Variables, only: fO3

        fO3 = 1.0
    end subroutine Calc_fO3_Ignore

    !==========================================================================
    ! Calculate fO3 for wheat
    !==========================================================================
    subroutine Calc_fO3_Wheat()
        use Variables, only: AFst0, fO3

        fO3 = ((1+(AFst0/11.5)**10)**(-1))
    end subroutine Calc_fO3_Wheat

    !==========================================================================
    ! Calculate fO3 for potato
    !==========================================================================
    subroutine Calc_fO3_Potato()
        use Variables, only: AOT0, fO3

        fO3 = ((1+(AOT0/40)**5)**(-1))
    end subroutine Calc_fO3_Potato

end module O3
