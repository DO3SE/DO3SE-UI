module Evapotranspiration

    public :: Calc_PEt, Calc_AEt, Calc_Ei, Calc_PEt_PM, Calc_AEt_PM

contains
    
    subroutine Calc_PEt()
        use Constants,  only: seaP, Ts_K
        use Inputs,     only: dd, VPD, Ts_c
        use Variables,  only: dd_prev, PEt, Rb, Gsto_PEt, LAI

        real :: PEt_hr = 0          ! Potential evapotranspiration for the hour
        real, save :: PEt_dd = 0    ! PEt for the day (accumulates)

        if ( LAI > 0 ) then
            PEt_hr = (VPD*3600*18)/(seaP*((Rb*0.61) &
                    +(((1/(Gsto_PEt/41000))*0.61)/LAI))*0.0224 &
                    *((Ts_c+Ts_K)/Ts_K)*(10**6))
        endif

        if ( dd == dd_prev ) then
            ! Same day, accumulate
            PEt_dd = PEt_dd + PEt_hr
        else                        
            ! Next day, store + reset
            PEt = PEt_dd
            PEt_dd = PEt_hr
        endif

    end subroutine Calc_PEt

    subroutine Calc_AEt()
        use Constants,  only: seaP, Ts_K
        use Inputs,     only: dd, VPD, Ts_c
        use Params_Veg, only: SWP_min
        use Variables,  only: dd_prev, AEt, SWP, Rb, Rsto, LAI

        real :: AEt_hr          ! Potential evapotranspiration for the hour
        real, save :: AEt_dd = 0    ! PEt for the day (accumulates)

        if ( LAI == 0 .or. SWP <= SWP_min ) then
            AEt_hr = 0
        else if ( LAI > 0 .or. SWP > SWP_min ) then
             AEt_hr = ((vpd)*3600*18)/(seaP*((Rb*0.61) &
                      +((Rsto*0.61)/LAI))*0.0224 &
                      *((Ts_c+Ts_K)/Ts_K)*10**6)
        endif

        if ( dd == dd_prev ) then
            ! Same day, accumulate
            AEt_dd = AEt_dd + AEt_hr
        else                        
            ! Next day, store + reset
            AEt = AEt_dd
            AEt_dd = AEt_hr
        endif

    end subroutine Calc_AEt

    subroutine Calc_Ei()
        use Constants,  only: seaP, Ts_K
        use Inputs,     only: dd, VPD, Ts_c
        use Variables,  only: dd_prev, Rb, Ei

        real :: Ei_hr
        real, save :: Ei_dd = 0

        Ei_hr = (VPD*3600*18)/(seaP*(Rb*0.61)*0.0224*((Ts_C+Ts_K)/Ts_K)*(10**6))

        if ( dd == dd_prev ) then
            ! Same day, accumulate
            Ei_dd = Ei_dd + Ei_hr
        else
            ! Next day, store + reset
            Ei = Ei_dd
            Ei_dd = Ei_hr
        endif
    end subroutine Calc_Ei

    subroutine Calc_PEt_PM()
        use Constants, only: Ts_K
        use Inputs, only: Ts_C, VPD, Rn, P
        use Variables, only: PEt, Ra, Rsto => Rsto_PEt

        real :: esat, eact, Tvir, delta, lambda, psychro, Pair, Cair, ET1, ET2, ET3

        ! TODO: optimise
        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        ! Convert from kPa to Pa
        esat = esat * 1000
        eact = esat - VPD
        Tvir = (Ts_c+Ts_K)/(1-(0.378*(eact/P)))
        delta= ((4098*esat)/((Ts_c+237.3)**2)) 
        lambda = (2501000-(2361*Ts_c))
        psychro = 1628.6 * (P/lambda)
        Pair = (0.003486*(P/Tvir))
        Cair = (0.622*((lambda*psychro)/P))
        
        ET1 = (Delta * Rn)
        ET2 = (3600 * Pair * Cair * (VPD / Ra)) / lambda
        ET3 = Delta + psychro * (1 + Rsto / Ra)

        PEt = (ET1 + ET2) / ET3

    end subroutine Calc_PEt_PM

    subroutine Calc_AEt_PM()
        use Constants, only: Ts_K
        use Inputs, only: Ts_C, VPD, Rn, P
        use Variables, only: PEt, Ra, Rsto

        real :: esat, eact, Tvir, delta, lambda, psychro, Pair, Cair, ET1, ET2, ET3

        ! TODO: optimise
        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        ! Convert from kPa to Pa
        esat = esat * 1000
        eact = esat - VPD
        Tvir = (Ts_c+Ts_K)/(1-(0.378*(eact/P)))
        delta= ((4098*esat)/((Ts_c+237.3)**2)) 
        lambda = (2501000-(2361*Ts_c))
        psychro = 1628.6 * (P/lambda)
        Pair = (0.003486*(P/Tvir))
        Cair = (0.622*((lambda*psychro)/P))
        
        ET1 = (Delta * Rn)
        ET2 = (3600 * Pair * Cair * (VPD / Ra)) / lambda
        ET3 = Delta + psychro * (1 + Rsto / Ra)

        AEt = (ET1 + ET2) / ET3

    end subroutine Calc_AEt_PM

end module Evapotranspiration
