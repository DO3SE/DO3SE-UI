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

    public :: Soil_initialise, Calc_precip, Calc_SWP

    real, private :: precip_dd

contains

    subroutine Soil_initialise()
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
        fSWP = (((-1) * SWP)** (-0.706)) * 0.355
        SMD = (Fc_m - Sn) * root
    end subroutine Soil_initialise

    subroutine Calc_SWP()
        use Constants, only: SWC_sat
        use Params_Site, only: Fc_m, soil_b, SWP_AE
        use Params_Veg, only: SWP_min, SWP_max, enable_fSWP, fmin, root
        use Inputs, only: dd, precip_acc
        use Variables, only: AEt, Es, Ei, LAI, SWP_min_vol
        use Variables, only: Sn, per_vol, ASW, SWP, fSWP, SMD
        use Variables, only: Sn_diff, P_input

        if (precip_acc > 0) then
            P_input = (precip_acc - (0.0001*LAI)) + ((0.0001*LAI) - min(Ei, 0.0001*LAI))
        else
            P_input = 0
        end if
        ! Can't lose water through Ei
        P_input = max(0.0, P_input)
        Sn_diff = (P_input - AEt - Es) / root

        ! Calculate new Sn, with field capacity as a maximum
        Sn = min(Fc_m, Sn + Sn_diff)
        per_vol = Sn * 100

        ! Calculate ASW and SWP for new water content
        ASW = (Sn - SWP_min_vol) * root
        SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

        ! Calculate SMD for new water content
        SMD = (Fc_m - Sn) * root

        ! fSWP enabled?
        if (enable_fSWP > 0) then
            fSWP = (((-1) * SWP)** (-0.706)) * 0.355
            fSWP = min(max(fSWP, fmin), 1.0)
        else
            ! Model is multiplicative, so fSWP = 1.0 removes its significance
            fSWP = 1.0
        end if
    end subroutine Calc_SWP

end module Soil
