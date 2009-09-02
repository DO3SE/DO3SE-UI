module Evapotranspiration

    public :: Calc_Penman_Monteith

contains

    !
    ! Calculate the evaporation of intercepted precipitation (Ei), potential and
    ! actual evapotranspiration (PEt and AEt) and soil evaporation (Es) using 
    ! the Penman-Monteith method.
    !
    subroutine Calc_Penman_Monteith()
        use Constants, only: seaP, Ts_K
        use Inputs, only: VPD, Ts_C, P, Rn, dd
        use Variables, only: Ei, AEt, PEt, Es, Rb, LAI, Rsto, Rsto_PEt, &
                             dd_prev, WC, Rsur
        use Params_Site, only: Fc_m

        real        :: VPD_Pa       ! VPD in Pa, not kPa
        real        :: esat, eact   ! esat and eact in Pa
        real        :: Tvir, delta, lambda, psychro, Pair, Cair, G
        
        real        :: Et_1, Et_2, Ei_3, PEt_3, AEt_3, Ei_hr, PEt_hr, AEt_hr
        real        :: t, Es_G, Es_1, Es_2, Es_3, Es_hr

        real, save  :: Ei_dd = 0, PEt_dd = 0, AEt_dd = 0, Es_dd = 0

        VPD_Pa = VPD * 1000

        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        esat = esat * 1000  ! Convert to Pa
        eact = esat - VPD_Pa

        Tvir = (Ts_c+Ts_K)/(1-(0.378*(eact/P)))
        delta= ((4098*esat)/((Ts_c+237.3)**2)) 
        lambda = (2501000-(2361*Ts_c))
        psychro = 1628.6 * (P/lambda)
        Pair = (0.003486*(P/Tvir))
        Cair = (0.622*((lambda*psychro)/P))

        G = 0.1 * Rn
        
        Et_1 = (delta * (Rn - G)) / lambda
        Et_2 = 3600 * Pair * Cair * VPD_Pa / (Rb * 0.61) / lambda

        Ei_3 = delta + psychro
        Ei_hr = (Et_1 + Et_2) / Ei_3 / 1000

        PEt_3 = delta + psychro * (1 + (Rsto_PEt * (0.61 / LAI)) / (Rb * 0.61))
        PEt_hr = (Et_1 + Et_2) / PEt_3 / 1000

        AEt_3 = delta * psychro * (1 + (Rsto * (0.61 / LAI)) / (Rb * 0.61))
        AEt_hr = (Et_1 + Et_2) / AEt_3 / 1000

        if (WC < Fc_m) then
            Es_hr = 0
        else
            t = exp(-0.5 * LAI)
            Es_G = Rn * t
            Es_1 = (delta * Es_G) / lambda
            Es_2 = 3600 * Pair * Cair * VPD_Pa / (Rsur * 0.61) / lambda
            Es_3 = delta + psychro
            Es_hr = (Es_1 + Es_2) / Es_3 / 1000
        endif

        if (dd == dd_prev) then
            ! Same day, accumulate
            Ei_dd = Ei_dd + Ei_hr
            PEt_dd = PEt_dd + PEt_hr
            AEt_dd = AEt_dd + AEt_hr
            Es_dd = Es_dd + Es_hr
        else
            ! Next day, store + reset
            Ei = Ei_dd
            Ei_dd = Ei_hr
            PEt = PEt_dd
            PEt_dd = PEt_hr
            AEt = AEt_dd
            AEt_dd = AEt_hr
            Es = Es_dd
            Es_dd = Es_hr
        endif
    end subroutine Calc_Penman_Monteith

end module Evapotranspiration
