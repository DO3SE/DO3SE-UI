module Evapotranspiration

    public :: Calc_PEt, Calc_AEt, Calc_Ei

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

end module Evapotranspiration
