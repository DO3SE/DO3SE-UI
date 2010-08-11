module R

    public :: Calc_Rext, Calc_Rsoil, Calc_Ra_Simple, Calc_Rb, Calc_Rgs, &
                Calc_Rinc, Calc_Gsto, Calc_Rsto, Calc_Rsur, &
                Calc_Ra_With_Heat_Flux

    ! VPD sum for the day (kPa)
    real, private, save :: VPD_dd = 0

contains

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance
    !==========================================================================
    subroutine Calc_Ra_Simple()
        use Constants, only: k, izR
        use Inputs, only: ustar
        use Parameters, only: h, d
        use Variables, only: Ra

        Ra = (1 / (ustar * k)) * log((izR - d) / (h - d))
    end subroutine Calc_Ra_Simple

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance, taking into account heat flux data
    !==========================================================================
    subroutine Calc_Ra_With_Heat_Flux()
        use Constants, only: Rmass, Ts_K, k, g, cp, pi, z => izR
        use Inputs, only: P, Hd, Ts_C, ustar
        use Variables, only: Ra
        use Parameters, only: d, zo

        real :: Tk, Ezo, Ezd, Psi_m_zd, Psi_m_zo, Psi_h_zd, Psi_h_zo, rho, L, &
                Xzo, Xzd

        Tk = Ts_C + Ts_K
        if (Hd == 0) then
            Hd = 0.000000000001
        end if

        ! Surface density of dry air (including conversion from to Pa to kPa)
        rho = (P * 1000) / (Rmass * Tk)

        ! Monin-Obukhov Length
        L = -(Tk * ustar**3 * rho * cp) / (k * g * Hd)

        Ezd = (z - d) / L
        Ezo = zo / L

        if (Ezd >= 0) then
            Psi_h_zd = -5 * Ezd
            Psi_m_zd = -5 * Ezd
        else
            Xzd = (1 - 15*Ezd)**(1.0/4.0)
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
        use Constants, only: k, v, DO3, DH2O, Pr
        use Inputs, only: ustar
        use Variables, only: Rb, Rb_H2O

        Rb = (2.0/(k*ustar)) * (((v/DO3)/Pr)**(2.0/3.0))
        Rb_H2O = (2.0/(k*ustar)) * (((v/DH2O)/Pr)**(2.0/3.0))
    end subroutine Calc_Rb

    !==========================================================================
    ! Calculate Rgs, non-vegetative surface resistance
    !==========================================================================
    subroutine Calc_Rgs()
        use Parameters, only: Rsoil
        use Variables, only: Rgs

        Rgs = Rsoil
    end subroutine Calc_Rgs

    !==========================================================================
    ! Calculate Rinc, in-canopy aerodynamic resistance
    !==========================================================================
    subroutine Calc_Rinc()
        use Parameters, only: Rinc_b, h
        use Inputs, only: ustar
        use Variables, only: SAI, Rinc

        Rinc = Rinc_b * SAI * h/ustar
    end subroutine Calc_Rinc

    !==========================================================================
    ! Calculate Rsto, stomatal resistance
    !==========================================================================
    subroutine Calc_Rsto()
        use Parameters, only: gmax, gmorph, fmin, VPD_crit
        use Inputs, only: VPD, dd
        use Variables, only: fphen, flight, ftemp, fVPD, fXWP, fO3, dd_prev
        use Variables, only: leaf_fphen, leaf_flight, LAI
        use Variables, only: Gsto_l, Rsto_l, Gsto, Rsto, Gsto_c, Rsto_c, &
                             Gsto_PEt, Rsto_PEt

        real :: Gsto_l_prev, Gsto_prev, Gsto_c_prev, Gsto_PEt_prev

        ! Preparation for VPD_crit limiting
        !   Copy old Gsto values
        Gsto_l_prev = Gsto_l
        Gsto_prev = Gsto
        Gsto_c_prev = Gsto_c
        Gsto_PEt_prev = Gsto_PEt
        !   Reset accumulated VPD?
        if (dd /= dd_prev) then
            VPD_dd = 0
        end if
        !   Accumulate VPD during daylight hours
        if (Flight > 0) then
            VPD_dd = VPD_dd + VPD
        end if

        ! Leaf Gsto
        Gsto_l = gmax * min(leaf_fphen, fO3) * leaf_flight * max(fmin, ftemp * fVPD * fXWP)
        ! Mean Gsto
        Gsto = (gmax * gmorph) * fphen * flight * max(fmin, ftemp * fVPD * fXWP)
        ! Estimate canopy Gsto from mean leaf Gsto
        Gsto_c = Gsto * LAI
        ! Potential canopy Gsto for PEt calculation (non-limiting SWP)
        Gsto_PEt = gmax * fphen * flight * ftemp * fVPD * LAI

        ! Check the VPD_crit condition
        if (VPD_dd >= VPD_crit) then
            Gsto_l = min(Gsto_l, Gsto_l_prev)
            Gsto = min(Gsto, Gsto_prev)
            Gsto_c = min(Gsto_c, Gsto_c_prev)
            Gsto_PEt = min(Gsto_PEt, Gsto_PEt_prev)
        end if

        ! Leaf Rsto
        if (Gsto_l <= 0) then
            Rsto_l = 100000
        else
            Rsto_l = 41000 / Gsto_l
        end if

        ! Mean Rsto
        if (Gsto <= 0) then
            Rsto = 100000
        else
            Rsto = 41000 / Gsto  ! Gsto in s/m = Gsto * 41000, Rsto = 1 / Gsto
        end if

        ! Canopy Rsto
        if (Gsto_c <= 0) then
            Rsto_c = 100000
        else
            Rsto_c = 41000 / Gsto_c
        end if

        ! Potential canopy Rsto for PEt calculation
        if (Gsto_PEt <= 0) then
            Rsto_PEt = 100000
        else
            Rsto_PEt = 41000 / Gsto_PEt
        end if
    end subroutine Calc_Rsto

    !==========================================================================
    !==========================================================================
    subroutine Calc_Rsur()
        use Parameters, only: Rext
        use Parameters, only: Rsoil
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
