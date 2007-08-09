module R_mod

    public :: Calc_Rext, Calc_Rsoil, Calc_ustar, Calc_Ra, Calc_Rb, Calc_Rgs, &
                Calc_Rinc, Calc_Gsto, Calc_Rsto, Calc_Rsur

contains

    !***************************************************************************
    ! Calculate ustar - resistance velocity
    !***************************************************************************
    subroutine Calc_ustar()
        use Constants_mod, only: uzR, d, zo, k
        use Inputs_mod, only: uh
        use Variables_mod, only: ustar

        ustar = (uh * k) / log((uzR - d) / (zo))
    end subroutine Calc_ustar
   

    !***************************************************************************
    ! Calculate Ra, Atmospheric resistance
    !***************************************************************************
    subroutine Calc_Ra()
        use Constants_mod, only: uzR, d, zo, k, h, czR
        use Variables_mod, only: ustar, Ra, Ra_O3

        if ( uzR < zo + d ) then
            Ra = 1 / (k * ustar) * (log(((zo + d) - d)/(h - d)))
        else
            Ra = 1 / (k * ustar) * (log((uzR - d)/(h - d)))
        end if

        if ( czR < d + zo ) then
            Ra_O3 = 1 / (k * ustar) * (log(((zo + d) - d)/(h - d)))
        else
            Ra_O3 = 1 / (k * ustar) * (log((czR - d)/(h - d)))
        end if
    end subroutine Calc_Ra

    !***************************************************************************
    ! Calculate Rb, quasi-laminar boundary layer resistance, s/m
    !***************************************************************************
    subroutine Calc_Rb()
        use Constants_mod, only: k, v, DO3, Pr
        use Variables_mod, only: ustar, Rb

        Rb = (2/(k*ustar)) * ((v/DO3/Pr)**(2/3))
    end subroutine Calc_Rb

    !***************************************************************************
    ! Calculate Rgs, non-vegetative surface resistance
    !***************************************************************************
    subroutine Calc_Rgs()
        use Params_Site_mod, only: Rsoil
        use Inputs_mod, only: Ts_c
        use Variables_mod, only: ustar, Rgs

        real :: Rlow    ! Low temperature resistance(af.Wesely, 1989)
 
        Rlow = (1000 * exp(-(Ts_c + 4)))
        ! TODO:   ????
        Rgs = Rsoil + Rlow + 2000*0
    end subroutine Calc_Rgs

    !***************************************************************************
    ! Calculate Rinc, in-canopy aerodynamic resistance
    !***************************************************************************
    subroutine Calc_Rinc()
        use Params_Veg_mod, only: Rinc_b
        use Variables_mod, only: ustar, SAI, Rinc

        Rinc = Rinc_b * SAI * Rinc_b/ustar
    end subroutine Calc_Rinc

    !***************************************************************************
    ! Calculate Rsto, stomatal resistance
    !***************************************************************************
    subroutine Calc_Rsto()
        use Params_Veg_mod, only: gmax, fmin
        use Variables_mod, only: fphen, flight, ftemp, fVPD, fSWP, Gsto, Gsto_PEt, Rsto, Rsto_PEt, SWP, LAI

        real :: Gsto_sm

        Gsto = gmax * fphen * flight * ftemp * fVPD * fSWP

        ! Gsto for PEt - assume non-limiting SWP
        Gsto_PEt = gmax * fphen * flight * ftemp * fVPD

        ! Rsto for PEt
        if ( Gsto_PEt == 0 .or. LAI == 0 ) then
            Rsto_PEt = 100000
        else
            Rsto_PEt = 1/((Gsto_PEt * LAI) / 41000)     ! potential bulk canopy 
                                                        ! stomatal resistance to 
                                                        ! O3 in s/m
        end if

        ! Rsto
        Gsto_sm = Gsto / 41000
        if ( Gsto_sm <= 0 ) then
            Rsto = 100000
        else
            Rsto = 1/(Gsto_sm)
        end if

        ! estimate whole canopy stomatal conductance from average leaf stomatal 
        ! conductance
        if ( LAI == 0 ) then
            Gsto = 0
        else if ( Gsto > 0 ) then
            Gsto = Gsto * LAI
        end if
    end subroutine Calc_Rsto

    subroutine Calc_Rsur()
        use Params_Veg_mod, only: Rext
        use Params_Site_mod, only: Rsoil
        use Variables_mod, only: LAI, SAI, Rsto, Rinc, Rsur
        
        if ( LAI > 0 ) then
            Rsur = 1 / ((LAI / Rsto) + (SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI > 0 ) then
            Rsur = 1 / ((SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI == 0 ) then
            ! surely this is Rsur = Rsoil ?
            Rsur = 1 / (1 / Rsoil)
        end if
    end subroutine Calc_Rsur

end module R_mod
