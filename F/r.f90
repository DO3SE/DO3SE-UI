module R

    public :: Calc_Rext, Calc_Rsoil, Calc_ustar, Calc_Ra, Calc_Rb, Calc_Rgs, &
                Calc_Rinc, Calc_Gsto, Calc_Rsto, Calc_Rsur, &
                Calc_Ra_With_Heat_Flux

contains

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance
    !==========================================================================
    subroutine Calc_Ra()
        use Constants, only: k, izR
        use Inputs, only: ustar
        use Params_Site, only: O3zR, O3_d
        use Params_Veg, only: h, d
        use Variables, only: Ra

        Ra = (1 / (ustar * k)) * log((izR - d) / (h - d))
    end subroutine Calc_Ra

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance, taking into account heat flux data
    !==========================================================================
    subroutine Calc_Ra_With_Heat_Flux()
        use Constants, only: Rmass, Ts_K, k, g, cp, pi
        use Inputs, only: P, Hd, Ts_C, ustar
        use Variables, only: Ra
        use Params_Site, only: z => uzR
        use Params_Veg, only: h, d, zo

        real :: Tk, Ezo, Ezd, Psi_m_zd, Psi_m_zo, Psi_h_zd, Psi_h_zo, rho, L, &
                Xzo, Xzd

        ! TODO: which heights are used where here?!?!

        Tk = Ts_C + Ts_K
        if (Hd == 0) then
            Hd = 0.000000000001
        end if

        ! Surface density of dry air
        rho = P / (Rmass * Tk)

        ! Monin-Obukhov Length
        L = -(Tk * ustar**3 * rho * cp) / (k * g * Hd)

        Ezd = (z - d) / L
        Ezo = zo / L

        if (Ezd >= 0) then
            Psi_h_zd = -5 * Ezd
            Psi_m_zd = -5 * Ezd
        else
            Xzd = (1 - 15*Ezd)**(1/4)
            Psi_m_zd = log(((1+Xzd**2)/2)*((1+Xzd)/2)**2)-2*ATAN(Xzd)+(PI/2)
            Psi_h_zd = 2*log((1+Xzd**2)/2)
        end if

        if (Ezo >= 0) then
            Psi_h_zo = -5*Ezo
            Psi_m_zo = -5*Ezo 
        else
            Xzo = (1-15*Ezo)**(0.25)
            Psi_m_zo = log(((1+Xzo**2)/2)*((1+Xzo)/2)**2)-2*ATAN(Xzo)+(PI/2)
            Psi_h_zo = 2*log((1+Xzo**2)/2)
        end if

        Ra = (1 / (k * ustar)) * (log((z - d) / zo) - Psi_h_zd + Psi_h_zo)
    end subroutine Calc_Ra_With_Heat_Flux

    !==========================================================================
    ! Calculate Rb, quasi-laminar boundary layer resistance, s/m
    !==========================================================================
    subroutine Calc_Rb()
        use Constants, only: k, v, DO3, Pr
        use Inputs, only: ustar
        use Variables, only: Rb

        Rb = (2/(k*ustar)) * ((v/DO3/Pr)**(2/3))
    end subroutine Calc_Rb

    !==========================================================================
    ! Calculate Rgs, non-vegetative surface resistance
    !==========================================================================
    subroutine Calc_Rgs()
        use Params_Site, only: Rsoil
        use Inputs, only: Ts_C, ustar
        use Variables, only: Rgs

        real :: Rlow    ! Low temperature resistance(af.Wesely, 1989)
 
        Rlow = (1000 * exp(-(Ts_c + 4)))
        ! TODO:   ????
        Rgs = Rsoil + Rlow + 2000*0
    end subroutine Calc_Rgs

    !==========================================================================
    ! Calculate Rinc, in-canopy aerodynamic resistance
    !==========================================================================
    subroutine Calc_Rinc()
        use Params_Veg, only: Rinc_b
        use Inputs, only: ustar
        use Variables, only: SAI, Rinc

        Rinc = Rinc_b * SAI * Rinc_b/ustar
    end subroutine Calc_Rinc

    !==========================================================================
    ! Calculate Rsto, stomatal resistance
    !==========================================================================
    subroutine Calc_Rsto()
        use Params_Veg, only: gmax, fmin
        use Variables, only: fphen, flight, ftemp, fVPD, fSWP, Gsto, Gsto_PEt, Rsto, Rsto_PEt, SWP, LAI

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

    !==========================================================================
    !==========================================================================
    subroutine Calc_Rsur()
        use Params_Veg, only: Rext
        use Params_Site, only: Rsoil
        use Variables, only: LAI, SAI, Rsto, Rinc, Rsur
        
        if ( LAI > 0 ) then
            Rsur = 1 / ((LAI / Rsto) + (SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI > 0 ) then
            Rsur = 1 / ((SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI == 0 ) then
            ! surely this is Rsur = Rsoil ?
            Rsur = 1 / (1 / Rsoil)
        end if
    end subroutine Calc_Rsur

end module R
