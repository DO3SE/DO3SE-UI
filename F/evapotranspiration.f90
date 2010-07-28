module Evapotranspiration

    public :: Calc_Penman_Monteith, Calc_Penman_Monteith_daily

    real, private :: Ei_dd = 0, PEt_dd = 0, Et_dd = 0, Es_dd = 0

contains

    !
    ! Calculate the evaporation of intercepted precipitation (Ei), potential
    ! plant transpiration (PEt), actual plant transpiration (Et), actual
    ! evapotranspiration (AEt) and soil evaporation (Es) using the
    ! Penman-Monteith method.
    !
    subroutine Calc_Penman_Monteith()
        use Constants, only: seaP, Ts_K
        use Inputs, only: VPD, Ts_C, P, dd, Rn_MJ => Rn
        use Variables, only: Ei, Et, PEt, AEt, Es, Rb_H2O, LAI, Rsto_c, &
                             Rsto_PEt, dd_prev, Sn, Rinc, Rgs
        use Params_Site, only: Fc_m
        use Variables, only: PEt_3, Et_3, Ei_hr, PEt_hr, Et_hr, Et_hr_prev, Es_hr

        real        :: VPD_Pa       ! VPD in Pa, not kPa
        real        :: P_Pa         ! Pressure in Pa, not kPa
        real        :: esat, eact   ! esat and eact in Pa
        real        :: Tvir, delta, lambda, psychro, Pair, Cair, G
        
        real        :: Et_1, Et_2, Ei_3 !, PEt_3, Et_3, Ei_hr, PEt_hr, Et_hr
        real        :: t, Es_Rn, Es_G, Es_1, Es_2, Es_3 !, Es_hr

        ! Convert Rn to J from MJ
        real :: Rn
        Rn = Rn_MJ * 1000000.0

        VPD_Pa = VPD * 1000
        P_Pa = P * 1000

        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        esat = esat * 1000  ! Convert to Pa
        eact = esat - VPD_Pa

        Tvir = (Ts_c+Ts_K)/(1-(0.378*(eact/P_Pa)))
        delta= ((4098*esat)/((Ts_c+237.3)**2)) 
        lambda = (2501000-(2361*Ts_c))
        psychro = 1628.6 * (P_Pa/lambda)
        Pair = (0.003486*(P_Pa/Tvir))
        Cair = (0.622*((lambda*psychro)/P_Pa))

        G = 0.1 * Rn
        
        Et_1 = (delta * (Rn - G)) / lambda
        Et_2 = 3600 * Pair * Cair * VPD_Pa / Rb_H2O / lambda

        Ei_3 = delta + psychro
        Ei_hr = (Et_1 + Et_2) / Ei_3 / 1000

        PEt_3 = delta + psychro * (1 + (Rsto_PEt * 0.61) / Rb_H2O)
        PEt_hr = (Et_1 + Et_2) / PEt_3 / 1000

        Et_3 = delta + psychro * (1 + (Rsto_c * 0.61) / Rb_H2O)
        Et_hr_prev = Et_hr
        Et_hr = (Et_1 + Et_2) / Et_3 / 1000

        if (Sn < Fc_m) then
            Es_hr = 0
        else
            t = exp(-0.5 * LAI)
            Es_Rn = Rn * t
            Es_G = 0.1 * Es_Rn
            Es_1 = (delta * (Es_Rn - Es_G)) / lambda
            Es_2 = 3600 * Pair * Cair * VPD_Pa / (Rgs + Rinc + Rb_H2O) / lambda
            Es_3 = delta + psychro
            Es_hr = (Es_1 + Es_2) / Es_3 / 1000
        endif

        Ei_dd = Ei_dd + Ei_hr
        PEt_dd = PEt_dd + PEt_hr
        Et_dd = Et_dd + Et_hr
        Es_dd = Es_dd + Es_hr
    end subroutine Calc_Penman_Monteith

    subroutine Calc_Penman_Monteith_daily()
        use Variables, only: Ei, PEt, Et, Es, AEt

        Ei = Ei_dd
        Ei_dd = 0
        PEt = PEt_dd
        PEt_dd = 0
        Et = Et_dd
        Et_dd = 0
        Es = Es_dd
        Es_dd = 0

        ! TODO: Calculate AEt correctly
        AEt = Et
    end subroutine Calc_Penman_Monteith_daily

end module Evapotranspiration
