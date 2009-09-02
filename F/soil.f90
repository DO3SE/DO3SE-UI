!
! Soil water calculations
!
! Terminology:
!   Fc_m    = Volumetric field capacity
!   Sn_star = Initial volumetric water content, <= Fc_m
!   Sn      = Current volumetric water content, <= Fc_m
!   Sn_diff = Today's volumetric water content change (+ve = gain)
!   SWP_min_vol = Minimum SWP for vegetation as volumetric content
!   ASW     = Available soil water (m), = Sn - SWP_min_vol
!   SWP     = Soil water potential (MPa)
!   per_vol = Volumetric water content as a percentage
!   SMD     = Soil moisture deficit (m), relative to field capacity
!
module Soil

    public :: Soil_initialize, Calc_precip, Calc_SWP

contains

    subroutine Soil_initialize()
        use Constants, only: SWC_sat
        use Params_Site, only: Fc_m, soil_b, SWP_AE
        use Params_Veg, only: SWP_min, SWP_max, fmin, root
        use Variables, only: SWP_min_vol, Sn_star, Sn, per_vol, ASW, SWP, fSWP, SMD

        ! Convert SWP_min to volumetric (MPa -> m^3/m^3)
        SWP_min_vol = 1.0 / (((SWP_min/SWP_AE)**(1.0/soil_b)) / SWC_sat)

        ! Volumetric water content, initially at field capacity
        Sn_star = Fc_m
        Sn = Sn_star

        ! As a percentage
        per_vol = Sn * 100

        ! ASW and SWP for initial volumetric water content
        ASW = (Sn - SWP_min_vol) * root
        SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

        ! Calculate fSWP and SMD for initial water content
        fSWP = max(fmin, ((1 - fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin))
        SMD = (Fc_m - Sn) * root
    end subroutine Soil_initialize

    subroutine Calc_SWP()
        use Constants, only: SWC_sat
        use Params_Site, only: Fc_m, soil_b, SWP_AE
        use Params_Veg, only: SWP_min, SWP_max, fmin, root
        use Inputs, only: dd
        use Variables, only: dd_prev, precip, AEt, Es, Ei, LAI, SWP_min_vol
        use Variables, only: Sn, per_vol, ASW, SWP, fSWP, SMD

        real :: Sn_diff

        ! Only once per day
        if (dd /= dd_prev) then
            if (precip == 0) then
                Sn_diff = (-AEt - Es) / root
            else
                Sn_diff = (precip - (0.0001*LAI)) &
                        + ((0.0001*LAI) - min(Ei, 0.0001*LAI)) / root
            endif

            ! Calculate new Sn, with field capacity as a maximum
            Sn = min(Fc_m, Sn + Sn_diff)
            per_vol = Sn * 100

            ! Calculate ASW and SWP for new water content
            ASW = (Sn - SWP_min_vol) * root
            SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

            ! Calculate fSWP and SMD for new water content
            fSWP = max(fmin, ((1 - fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin))
            SMD = (Fc_m - Sn) * root
        endif
    end subroutine Calc_SWP

    subroutine Calc_precip()
        use Inputs, only: dd, precip_in => precip
        use Variables, only: dd_prev, precip

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

end module Soil
