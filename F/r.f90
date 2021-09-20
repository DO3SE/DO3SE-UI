module R

    public :: Calc_Ra_Simple, Calc_Rb, Calc_Rgs, &
                Calc_Rinc, Calc_Rsur, Calc_Ra_With_Heat_Flux

    public :: ra_simple, rb, rsto_from_gsto

    public :: Calc_Gsto_Multiplicative, Calc_Rsto, VPDcrit_prepare, VPDcrit_apply

    ! VPD sum for the day (kPa)
    real, private, save :: VPD_dd = 0
    real, private, save :: Gsto_l_prev, Gsto_prev, Gsto_c_prev, Gsto_PEt_prev, Gsun_l_prev

contains

    function ra_simple(ustar, z1, z2, d) result (ra)
        real, intent(in) :: ustar   ! Friction velocity (m/s)
        real, intent(in) :: z1      ! Lower height (m)
        real, intent(in) :: z2      ! Upper height (m)
        real, intent(in) :: d       ! Zero displacement height (m)

        real :: ra                  ! Output: aerodynamic resistance (s/m)

        real, parameter :: K = 0.41 ! von Karman's constant

        ra = (1.0 / (ustar * K)) * log((z2 - d) / (z1 - d))
    end function ra_simple

    function rsto_from_gsto(gsto, Ts_C) result (rsto)
        real, intent(in) :: gsto    ! Stomatal conductance (mmol m-2 s-1)
        real, intent(in) :: Ts_C    ! Tile temperature (degrees C)
        real :: rsto                ! Output: stomatal resistance (
        real :: mmol2sm
        real, parameter :: MAX_RSTO = 100000
        real, parameter :: Ts_K = 273.15


        mmol2sm = 8.3144e-8 * (Ts_C + Ts_K) ! should this be kelvin?

        ! (gsto in m s-1) = 41000 * (gsto in mmol m-2 s-1)
        ! (rsto in s m-1) = 1 / (gsto in m s-1)
        ! mmol to m/s conversion from EMEP
        rsto = min(MAX_RSTO, 1 / (gsto * mmol2sm))
    end function rsto_from_gsto

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance
    !==========================================================================
    subroutine Calc_Ra_Simple()
        use Constants, only: k, izR
        use Inputs, only: ustar
        use Parameters, only: h, d
        use Variables, only: Ra

        Ra = ra_simple(ustar, h, izR, d)
    end subroutine Calc_Ra_Simple

    !==========================================================================
    ! Calculate Ra, Atmospheric resistance, taking into account heat flux data
    ! Ref: Garratt, 1994, pp.55-58
    ! Ref: EMEP MSC-W Chemical transport Model
    !==========================================================================
    subroutine Calc_Ra_With_Heat_Flux()
        use Constants, only: k, pi, z => izR
        use Inputs, only: ustar, L
        use Variables, only: Ra
        use Parameters, only: d, zo

        real :: Ezo, Ezd, Psi_m_zd, Psi_m_zo, Psi_h_zd, Psi_h_zo, &
                Xzo_m, Xzd_m, Xzo_h, Xzd_h


        Ezd = (z - d) / L
        Ezo = zo / L

        if (Ezd >= 0) then
            Psi_h_zd = -5 * Ezd
            Psi_m_zd = -5 * Ezd
        else
            Xzd_m = (1 - 16*Ezd)**(1.0/4.0)
            Xzd_h = (1 - 16*Ezd)**(1.0/2.0)
            Psi_m_zd = log(((1+Xzd_m**2)/2)*((1+Xzd_m)/2)**2)-2*ATAN(Xzd_m)+(PI/2)
            Psi_h_zd = 2*log((1+Xzd_h**2)/2)
        end if

        if (Ezo >= 0) then
            Psi_h_zo = -5*Ezo
            Psi_m_zo = -5*Ezo
        else
            Xzo_m = (1-16*Ezo)**(1.0/4.0)
            Xzo_h = (1-16*Ezo)**(1.0/2.0)
            Psi_m_zo = log(((1+Xzo_m**2)/2)*((1+Xzo_m)/2)**2)-2*ATAN(Xzo_m)+(PI/2)
            Psi_h_zo = 2*log((1+Xzo_h**2)/2)
        end if

        Ra = (1 / (k * ustar)) * (log((z - d) / zo) - Psi_h_zd + Psi_h_zo)
    end subroutine Calc_Ra_With_Heat_Flux


    function rb(ustar, d) result (rb_out)
        real, intent(in) :: ustar   ! Friction velocity (m/s)
        real, intent(in) :: d       ! Molecular diffusivity of substance in air (m2/s)

        real, parameter :: PR = 0.72    ! Prandtl number
        real, parameter :: K = 0.41     ! von Karman's constant
        real, parameter :: V = 0.000015 ! Kinematic viscosity of air at 20 C (m2/s)

        real :: rb_out              ! Output: Rb (s/m)

        rb_out = (2.0 / (K * ustar)) * (((V/d)/PR)**(2.0/3.0))
    end function rb

    !==========================================================================
    ! Calculate Rb, quasi-laminar boundary layer resistance, s/m
    !==========================================================================
    subroutine Calc_Rb()
        use Constants, only: DO3, DH2O
        use Inputs, only: ustar
        use Variables, only: Rb_out => Rb, Rb_H2O

        Rb_out = rb(ustar, DO3)
        Rb_H2O = rb(ustar, DH2O)
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
        use Inputs, only: VPD, dd, R
        use Variables, only: dd_prev, Gsto_l, Gsto, Gsto_c, Gsto_PEt, Gsun_l

        ! Copy old Gsto values
        Gsto_l_prev = Gsto_l
        Gsun_l_prev = Gsun_l
        Gsto_prev = Gsto
        Gsto_c_prev = Gsto_c
        Gsto_PEt_prev = Gsto_PEt

        ! Reset accumulated VPD at start of new day
        if (dd /= dd_prev) then
            VPD_dd = 0
        end if
        ! Accumulate VPD during daylight hours
        if (R > 50.0) then
            VPD_dd = VPD_dd + VPD
        end if
    end subroutine VPDcrit_prepare

    ! Limit Gsto values if accumulated VPD exceeds VPD_crit
    subroutine VPDcrit_apply()
        use Parameters, only: VPD_crit
        use Variables, only: Gsto_l, Gsto, Gsto_c, Gsto_PEt, Gsun_l

        if (VPD_dd >= VPD_crit) then
            ! Limit values to previous hour's Gsto
            Gsto_l = min(Gsto_l, Gsto_l_prev)
            Gsun_l = min(Gsun_l, Gsun_l_prev)
            Gsto = min(Gsto, Gsto_prev)
            Gsto_c = min(Gsto_c, Gsto_c_prev)
            Gsto_PEt = min(Gsto_PEt, Gsto_PEt_prev)
        end if
    end subroutine VPDcrit_apply

    !==========================================================================
    ! Calculate Rsto, stomatal resistance
    !==========================================================================
    subroutine Calc_Gsto_Multiplicative()
        use Parameters, only: gmax, gmorph, fmin
        use Variables, only: fphen, flight, ftemp, fVPD, fXWP, fO3, f_sun
        use Variables, only: leaf_fphen, leaf_flight, LAI
        use Variables, only: Gsto_l, Gsun_l, Gsto, Gsto_c, Gsto_PEt, Gsun_l_ms

        use Inputs, only: Ts_C
        use constants, only: Ts_K

        REAL :: mmol2sm

        mmol2sm = 8.3144e-8 * (Ts_C + Ts_K)

        ! Leaf Gsto
        Gsto_l = gmax * min(leaf_fphen, fO3) * leaf_flight * max(fmin, ftemp * fVPD * fXWP)
        ! Leaf sunlit gsto
        Gsun_l = gmax * min(fphen, fO3) * f_sun * max(fmin, ftemp * fVPD * fXWP)
        Gsun_l_ms = gmax * min(fphen, fO3) * f_sun * max(fmin, ftemp * fVPD * fXWP) *mmol2sm
        ! Mean Gsto
        Gsto = (gmax * gmorph) * fphen * flight * max(fmin, ftemp * fVPD * fXWP)
        ! Estimate canopy Gsto from mean leaf Gsto
        Gsto_c = Gsto * LAI
        ! Potential canopy Gsto for PEt calculation (non-limiting SWP)
        Gsto_PEt = gmax * fphen * flight * ftemp * fVPD * LAI
    end subroutine Calc_Gsto_Multiplicative

    subroutine Calc_Rsto()
        use Variables, only: Gsto_l, Rsto_l, Gsto, Rsto, Gsto_c, Rsto_c, Gsto_PEt, Rsto_PEt, Gsun_l, Rsun_l
        use Inputs, only: Ts_C

        ! Leaf Rsto
        Rsto_l = rsto_from_gsto(Gsto_l, Ts_C)
        ! Leaf sunlit Rsto
        Rsun_l = rsto_from_gsto(Gsun_l, Ts_C)
        ! Mean Rsto
        Rsto = rsto_from_gsto(Gsto, Ts_C)
        ! Canopy Rsto
        Rsto_c = rsto_from_gsto(Gsto_c, Ts_C)
        ! Potential canopy Rsto for PEt calculation
        Rsto_PEt = rsto_from_gsto(Gsto_PEt, Ts_C)
    end subroutine Calc_Rsto

    !==========================================================================
    !==========================================================================
    subroutine Calc_Rsur()
        use Parameters, only: Rext
        use Parameters, only: Rsoil
        use Variables, only: LAI, SAI, Rsto_c, Rinc, Rsur

        if ( LAI > 0 ) then
            Rsur = 1 / ((1 / Rsto_c) + (SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI > 0 ) then
            Rsur = 1 / ((SAI / Rext) + (1 / (Rinc + Rsoil)))
        else if ( SAI == 0 ) then
            ! surely this is Rsur = Rsoil ?
            Rsur = 1 / (1 / Rsoil)
        end if
    end subroutine Calc_Rsur

end module R
