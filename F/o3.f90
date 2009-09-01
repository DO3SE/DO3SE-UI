module O3

    public :: Calc_O3_Concentration, Calc_Ftot
    public :: Calc_Fst, Calc_AFstY, Calc_AOT40

contains

    !==========================================================================
    ! Calculate the ozone concentration at the canopy
    !
    ! This procedure results in the calculation of deposition velocity (Vd) and
    ! the ozone concentration at the canopy in both parts-per-billion and 
    ! nmol/m^3
    !==========================================================================
    subroutine Calc_O3_Concentration()
        use Constants, only: k, izR, v, DO3, Pr
        use Inputs, only: O3_ppb_zR, uh_i
        use Variables, only: O3_ppb, O3_nmol_m3, Ra, Rb, Rsur, Ra_i, Vd
        use Params_Site, only: O3zR, O3_d, O3_zo

        real :: ustar_o, O3_i, Rb_i, Vd_i

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
        O3_i = O3_ppb_zR / (1 - (Ra_i * Vd_i))

        O3_ppb = O3_i * (1 - (Ra * Vd))

        O3_nmol_m3 = O3_ppb * 41.67   ! Estimates ozone concentration at canopy height 
                                      ! in nmol/m3; N.B> need to do proper conversion
                                      ! to include changes in T and P but no P in flux tower data......
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
        use Constants, only: k
        use Params_Veg, only: gmax, Lm
        use Inputs, only: uh
        use Variables, only: Fst, leaf_fphen, leaf_flight, ftemp, fVPD, &
            fSWP, O3_nmol_m3

        real :: gO3, leaf_rb, leaf_gb, leaf_r
        real :: leaf_gO3, leaf_rO3 ! leaf stomatal conductance/resistance
        
        gO3 = gmax * leaf_fphen * leaf_flight * ftemp * fVPD * fSWP  ! in mmol O3 m^-2 s^-1

        leaf_rb = 1.3 * 150 * sqrt(Lm/uh)   ! leaf boundary layer resistance in s/m
        leaf_gb = 1 / leaf_rb               ! leaf boundary layer conductance in m/s
        
        if ( gO3 > 0 ) then
            leaf_gO3 = gO3 / 41000  ! leaf stomatal conductance in m/s
            leaf_rO3 = 1 / leaf_gO3 ! leaf stomatal resistance in s/m

            leaf_r = 1.0 / (leaf_gO3 + (1.0/2500.0))  ! leaf resistance in s/m

            if ( leaf_fphen > 0 ) then
                Fst = O3_nmol_m3 * leaf_gO3 * (leaf_r/(leaf_rb + leaf_r))  ! Fst in nmol/m2/s
            end if

        else if ( gO3 == 0 ) then
            Fst = 0
        end if

    end subroutine Calc_Fst

    !==========================================================================
    ! Calculate the accumulated stomatal flux above threshold Y
    !==========================================================================
    subroutine Calc_AFstY()
        use Variables, only: Fst, AFstY
        use Params_Veg, only: Y

        if ( Fst > Y ) then
            AFstY = AFstY + (((Fst - Y)*60*60)/1000000) ! Cumulative Fst above Y in mmol/m2
        end if
    end subroutine Calc_AFstY

    !==========================================================================
    ! Calculate the accumulated OT40
    !==========================================================================
    subroutine Calc_AOT40()
        use Variables, only: OT40, AOT40, O3_ppb, fphen
        use Inputs, only: R

        if ( O3_ppb > 40 ) then
            OT40 = (O3_ppb - 40) / 1000
        else
            OT40 = 0
        end if

        if ( R == 0 .or. fphen == 0 ) then
            OT40 = 0
        end if

        AOT40 = (AOT40 + OT40)
    end subroutine Calc_AOT40

end module O3
