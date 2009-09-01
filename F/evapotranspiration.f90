module Evapotranspiration

    public :: Calc_Ei_PEt_AEt_PM

contains

    subroutine Calc_Ei_PEt_AEt_PM()
        use Constants, only: seaP, Ts_K
        use Inputs, only: VPD, Ts_C, P, Rn, dd
        use Variables, only: Ei, AEt, PEt, Rb, LAI, Rsto, Rsto_PEt, dd_prev

        real        :: VPD_Pa       ! VPD in Pa, not kPa
        real        :: esat, eact   ! esat and eact in Pa
        real        :: Tvir, delta, lambda, psychro, Pair, Cair, G
        
        real        :: Et_1, Et_2, Ei_3, PEt_3, AEt_3, Ei_hr, PEt_hr, AEt_hr

        real, save  :: Ei_dd = 0, PEt_dd = 0, AEt_dd = 0

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

        if (dd == dd_prev) then
            ! Same day, accumulate
            Ei_dd = Ei_dd + Ei_hr
            PEt_dd = PEt_dd + PEt_hr
            AEt_dd = AEt_dd + AEt_hr
        else
            ! Next day, store + reset
            Ei = Ei_dd
            Ei_dd = Ei_hr
            PEt = PEt_dd
            PEt_dd = PEt_hr
            AEt = AEt_dd
            AEt_dd = AEt_hr
        endif
    end subroutine Calc_Ei_PEt_AEt_PM

end module Evapotranspiration
