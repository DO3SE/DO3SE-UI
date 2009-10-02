module O3

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
    !==========================================================================
    subroutine Calc_O3_Concentration()
        use Constants, only: k, izR, v, DO3, Pr, Ts_K
        use Inputs, only: O3_ppb_zR, uh_i, Ts_C, P
        use Variables, only: O3_ppb_i, O3_ppb, O3_nmol_m3, Ra, Rb, Rsur, Ra_i, Vd
        use Params_Site, only: O3zR, O3_d, O3_zo

        real, parameter :: R = 8.314510     ! Universal gas constant (J/K/mol)
        real, parameter :: M_O3 = 48.0      ! Molecular weight of O3 (g)

        real :: ustar_o, Rb_i, Vd_i, Vn

        ! Deposition velocity over target veg
        ! (we assume that this is "close enough" for over the measurement veg.)
        Vd = 1 / (Ra + Rb + Rsur)

        ! ustar over O3 measurement vegetation
        ustar_o = (uh_i * k) / log((izR - O3_d) / O3_zo)
        ! Ra over O3 measurement veg.
        Ra_i = (1 / (ustar_o * k)) * log((izR - O3_d) / (O3zR - O3_d))
        ! Rb over O3 measurement veg.
        Rb_i = (2.0/(k*ustar_o)) * (((v/DO3)/Pr)**(2.0/3.0))
        ! Estimated deposition velocity over O3 measurement veg.
        Vd_i = 1 / (Ra_i + Rb_i + Rsur)

        ! O3 concentration at intermediate height
        O3_ppb_i = O3_ppb_zR / (1 - (Ra_i * Vd_i))

        O3_ppb = O3_ppb_i * (1 - (Ra * Vd))

        ! Specific molar volume of an ideal gas at current temp + pressure
        Vn = R * ((Ts_C + Ts_K) / P)
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
        use Params_Veg, only: Lm, Rext
        use Inputs, only: uh
        use Variables, only: Gsto_l, Rsto_l, O3_nmol_m3, Fst

        real :: leaf_rb, leaf_r


        if (Gsto_l > 0) then
            leaf_rb = 1.3 * 150 * sqrt(Lm/uh)   ! leaf boundary layer resistance (s/m)
            leaf_r = 1.0 / ((1.0/Rsto_l) + (1.0/Rext))  ! leaf resistance in s/m
            Fst = O3_nmol_m3 * (1/Rsto_l) * (leaf_r / (leaf_rb + leaf_r))
        else
            Fst = 0
        end if
    end subroutine Calc_Fst

    !==========================================================================
    ! Calculate the accumulated stomatal flux above threshold Y
    !==========================================================================
    subroutine Calc_AFstY()
        use Variables, only: Fst, AFstY, AFst0
        use Params_Veg, only: Y

        ! Fst == 0 if Gsto_l == 0 (and Gsto_l == 0 if leaf_fphen == 0), so no
        ! need to check leaf_fphen
        AFst0 = AFst0 + ((Fst*60*60)/1000000)
        AFstY = AFstY + ((max(0.0, Fst - Y)*60*60)/1000000)
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
