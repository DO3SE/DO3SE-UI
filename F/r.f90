module R

    public :: Calc_Ra_Simple, Calc_Rb, Calc_Rgs, &
                Calc_Rinc, Calc_Rsur, Calc_Ra_With_Heat_Flux

    public :: Calc_Gsto_Multiplicative, Calc_Rsto, VPDcrit_prepare, VPDcrit_apply

    ! VPD sum for the day (kPa)
    real, private, save :: VPD_dd = 0
    real, private, save :: Gsto_l_prev, Gsto_prev, Gsto_c_prev, Gsto_PEt_prev

contains

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance
    !==========================================================================
    subroutine Calc_Ra_Simple()
        use Constants, only: k, izR
        use Inputs, only: ustar
        use Parameters, only: h, d
        use Variables, only: Ra

        use do3se_resistance, only: do3se_Ra_simple

        Ra = do3se_Ra_simple(ustar, h, izR, d)
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
        use Constants, only: DO3, DH2O
        use Inputs, only: ustar
        use Variables, only: Rb_out => Rb, Rb_H2O

        use do3se_resistance, only: do3se_Rb

        Rb_out = do3se_Rb(ustar, DO3)
        Rb_H2O = do3se_Rb(ustar, DH2O)
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


    ! Store previous hour's Gsto values, calculate accumulated VPD
    subroutine VPDcrit_prepare()
        use Inputs, only: VPD, dd
        use Variables, only: dd_prev, Flight, Gsto_l, Gsto, Gsto_c, Gsto_PEt

        ! Copy old Gsto values
        Gsto_l_prev = Gsto_l
        Gsto_prev = Gsto
        Gsto_c_prev = Gsto_c
        Gsto_PEt_prev = Gsto_PEt

        ! Reset accumulated VPD at start of new day
        if (dd /= dd_prev) then
            VPD_dd = 0
        end if
        ! Accumulate VPD during daylight hours
        if (Flight > 0) then
            VPD_dd = VPD_dd + VPD
        end if
    end subroutine VPDcrit_prepare

    ! Limit Gsto values if accumulated VPD exceeds VPD_crit
    subroutine VPDcrit_apply()
        use Parameters, only: VPD_crit
        use Variables, only: dd_prev, Flight, Gsto_l, Gsto, Gsto_c, Gsto_PEt

        if (VPD_dd >= VPD_crit) then
            ! Limit values to previous hour's Gsto
            Gsto_l = min(Gsto_l, Gsto_l_prev)
            Gsto = min(Gsto, Gsto_prev)
            Gsto_c = min(Gsto_c, Gsto_c_prev)
            Gsto_PEt = min(Gsto_PEt, Gsto_PEt_prev)
        end if
    end subroutine VPDcrit_apply


    pure subroutine do3se_gsto_mult(fphen, leaf_fphen, flight, leaf_flight, ftemp, &
                                    fVPD, fSWP, fO3, LAI, gmax, gmorph, fmin, &
                                    Gsto_l, Gsto, Gsto_c, Gsto_PEt)
        real, intent(in)    :: fphen        ! Phenology-related effect on gsto (fraction)
        real, intent(in)    :: leaf_fphen   ! Phenology-related effect on leaf gsto (fraction)
        real, intent(in)    :: flight       ! Irradiance effect on gsto (fraction)
        real, intent(in)    :: leaf_flight  ! Irradiance effect on leaf gsto (fraction)
        real, intent(in)    :: ftemp        ! Temperature effect on gsto (fraction)
        real, intent(in)    :: fVPD         ! VPD effect on gsto (fraction)
        real, intent(in)    :: fSWP         ! Soil water effect on gsto (fraction)
        real, intent(in)    :: fO3          ! O3 effect on gsto (fraction)
        real, intent(in)    :: LAI          ! Leaf area index, for bulk gsto (m^2/m^2)
        real, intent(in)    :: gmax         ! Maximum gsto (mmol O3 m-2 PLA s-1)
        real, intent(in)    :: gmorph       ! Sun/shade morphology factor (fraction)
        real, intent(in)    :: fmin         ! Minimum gsto fraction (fraction)

        real, intent(out)   :: Gsto_l       ! Output: leaf gsto (mmol O3 m-2 PLA s-1)
        real, intent(out)   :: Gsto         ! Output: mean canopy gsto (mmol O3 m-2 PLA s-1)
        real, intent(out)   :: Gsto_c       ! Output: bulk canopy gsto (mmol O3 m-2 PLA s-1)
        real, intent(out)   :: Gsto_PEt     ! Output: bulk canopy gsto assuming no soil water
                                            !         influence (mmol O3 m-2 PLA s-1)

        Gsto_l = gmax * min(leaf_fphen, fO3) * leaf_flight * max(fmin, ftemp * fVPD * fSWP)
        Gsto = (gmax * gmorph) * fphen * flight * max(fmin, ftemp * fVPD * fSWP)
        Gsto_c = Gsto * LAI
        Gsto_PEt = gmax * fphen * flight * ftemp * fVPD * LAI
    end subroutine do3se_gsto_mult

    !==========================================================================
    ! Calculate Rsto, stomatal resistance
    !==========================================================================
    subroutine Calc_Gsto_Multiplicative()
        use Parameters, only: gmax, gmorph, fmin
        use Variables, only: fphen, flight, ftemp, fVPD, fXWP, fO3
        use Variables, only: leaf_fphen, leaf_flight, LAI
        use Variables, only: Gsto_l, Gsto, Gsto_c, Gsto_PEt

        call do3se_gsto_mult(fphen, leaf_fphen, flight, leaf_flight, ftemp, &
                             fVPD, fXWP, fO3, LAI, gmax, gmorph, fmin, &
                             Gsto_l, Gsto, Gsto_c, Gsto_PEt)
    end subroutine Calc_Gsto_Multiplicative

    subroutine Calc_Rsto()
        use Variables, only: Gsto_l, Rsto_l, Gsto, Rsto, Gsto_c, Rsto_c, Gsto_PEt, Rsto_PEt

        use do3se_utils, only: do3se_rsto_from_gsto

        ! Leaf Rsto
        Rsto_l = do3se_rsto_from_gsto(Gsto_l)
        ! Mean Rsto
        Rsto = do3se_rsto_from_gsto(Gsto)
        ! Canopy Rsto
        Rsto_c = do3se_rsto_from_gsto(Gsto_c)
        ! Potential canopy Rsto for PEt calculation
        Rsto_PEt = do3se_rsto_from_gsto(Gsto_PEt)
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
