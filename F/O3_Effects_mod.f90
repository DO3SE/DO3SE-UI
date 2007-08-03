module O3_Effects_mod

    public :: Calc_Fst, Calc_AFstY, Calc_AOT40

contains
    
    subroutine Calc_Fst()
        use Inputs_mod, only: uh
        use Variables_mod, only: Fst, leaf_fphen, leaf_flight, ftemp, fVPD, &
            fSWP, O3_nmol_m3
        use Params_Veg_mod, only: gmax, Lm

        real :: gO3, leaf_rb, leaf_gb, leaf_r
        real :: leaf_gO3, leaf_rO3 ! leaf stomatal conductance/resistance

        gO3 = gmax * leaf_fphen * leaf_flight * ftemp * fVPD * fSWP  ! in mmol O3 m^-2 s^-1

        leaf_rb = 1.3 * 150 * sqrt(Lm/uh)   ! leaf boundary layer resistance in s/m
        leaf_gb = 1 / leaf_rb               ! leaf boundary layer conductance in m/s
        
        if ( gO3 > 0 ) then
            leaf_gO3 = gO3 / 41000  ! leaf stomatal conductance in m/s
            leaf_rO3 = 1 / leaf_gO3 ! leaf stomatal resistance in s/m

            leaf_r = 1 / (leaf_gO3 + (1/2500))  ! leaf resistance in s/m

            if ( leaf_fphen > 0 ) then
                Fst = O3_nmol_m3 * leaf_gO3 * (leaf_r/(leaf_rb + leaf_r))  ! Fst in nmol/m2/s
            end if

        else if ( gO3 == 0 ) then
            Fst = 0
        end if

    end subroutine Calc_Fst

    subroutine Calc_AFstY()
        use Variables_mod, only: Fst, AFstY
        use Params_Veg_mod, only: Y

        if ( Fst > Y ) then
            AFstY = AFstY + (((Fst - Y)*60*60)/1000000) ! Cumulative Fst above Y in mmol/m2
        end if
    end subroutine Calc_AFstY

    subroutine Calc_AOT40()
        use Variables_mod, only: AOT40, O3_ppb, fphen
        use Inputs_mod, only: Idfuse

        real :: OT40

        if ( O3_ppb > 40 ) then
            OT40 = (O3_ppb - 40) / 1000
        else
            OT40 = 0
        end if

        if ( Idfuse == 0 .or. fphen == 0 ) then
            OT40 = 0
        end if

        AOT40 = (AOT40 + OT40)
    end subroutine Calc_AOT40

end module O3_Effects_mod
