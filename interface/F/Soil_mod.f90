module Soil_mod

    public :: Soil_initialize, Calc_precip, Calc_SWP, Calc_fSWP

contains

    subroutine Soil_initialize()
        use Params_Site_mod, only: &
            Rsoil, soil_BD, soil_a, soil_b, Fc_m
        use Params_Veg_mod, only: &
            SWP_min, SWP_max
        use Variables_mod, only: PWP, ASW, Sn_star, Sn, SWP, WC, per_vol, fSWP, precip, &
            AEt, PEt, Ei, SMD

        ! Calculate Wstar
        PWP = soil_BD*((SWP_min/(soil_a*(0.01)))*1000)**(1/soil_b)
        ASW = Fc_m - PWP
        Sn_star = ASW

        ! Initialise other variables
        SWP         = (soil_a*0.01)*((Fc_m/soil_BD))**soil_b/1000
        Sn          = Sn_star
        WC          = Fc_m - PWP
        per_vol     = (Fc_m + PWP) * 100 
        fSWP        = 1
        precip = 0
        SMD = 0
    end subroutine Soil_initialize

    subroutine Calc_precip()
        use Inputs_mod, only: dd, precip_in => precip
        use Variables_mod, only: dd_prev, precip

        real, save :: precip_dd = 0

        if ( dd == dd_prev ) then
            ! Same day, accumulate (converts mm to m)
            precip_dd = precip_dd + (precip_in/1000)
        else
            ! Next day, store and reset
            precip = precip_dd
            precip_dd = precip_in/1000
        endif
    end subroutine Calc_precip

    subroutine Calc_SWP()
        use Inputs_mod, only: dd
        use Params_Veg_mod, only: root, SWP_min
        use Params_Site_mod, only: Fc_m, soil_BD, soil_a, soil_b
        use Variables_mod, only: dd_prev, AEt, Ei, Sn, SMD, WC, per_vol, SWP, precip, PWP, Sn_star

        real :: Sn_diff

        ! These only change once per day
        if ( dd /= dd_prev ) then
            if ( precip == 0 ) then
                Sn_diff = -((AEt)/root)
            else
                Sn_diff = (precip * 0.3) + ((precip * 0.7) - (min(Ei, (precip * 0.7)))) / root
            end if

            Sn = min(Sn_star, Sn + Sn_diff)
            SMD = Sn_star - Sn
            WC = Fc_m - (SMD)
            per_vol = ((Fc_m - SMD) + PWP) * 100
            SWP = (soil_a * 0.01) * ((WC/soil_BD))**soil_b/1000
        end if
    end subroutine Calc_SWP

    subroutine Calc_fSWP()
        use Variables_mod, only: SWP, fSWP
        fswp=1/(0.75+(SWP/(-0.25))**1.7)   ! sloped fSWP relationship better fit to wheat data
                                     ! (used to parameterise model)

        ! If using default DO3SE model use:

        !fswp = (1-fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin
        !fsWP = max(fswp, fmin)

        if (fswp > 1) then
            fswp = 1
        end if
    end subroutine Calc_fSWP

end module Soil_mod
