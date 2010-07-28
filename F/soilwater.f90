!
! Soil water calculations
!
! Terminology:
!   Fc_m    = Volumetric field capacity
!   Sn_star = Initial volumetric water content, <= Fc_m
!   Sn      = Current volumetric water content, <= Fc_m
!   P_input = Preciptation input (after evaporation of intercepted)
!   Sn_diff = Today's volumetric water content change (+ve = gain)
!   SWP_min_vol = Minimum SWP for vegetation as volumetric content
!   ASW     = Available soil water (m), = Sn - SWP_min_vol
!   SWP     = Soil water potential (MPa)
!   per_vol = Volumetric water content as a percentage
!   SMD     = Soil moisture deficit (m), relative to field capacity
!
module SoilWater

    public :: Init_SoilWater
    public :: Calc_Penman_Monteith
    public :: Calc_Penman_Monteith_daily
    public :: Calc_SWP

    ! Hourly intermediate
    real, public :: Ei_hr
    real, public :: Es_hr
    real, public :: PEt_hr
    real, public :: Et_hr
    real, public :: Et_hr_prev
    real, public :: PEt_3
    real, public :: Et_3

    ! Daily accumulation variables
    real, private :: Ei_dd, PEt_dd, Et_dd, Es_dd

contains
    
    subroutine Init_SoilWater()
        use Constants, only: SWC_sat
        use Params_Site, only: Fc_m, soil_b, SWP_AE
        use Params_Veg, only: SWP_min, SWP_max, fmin, root
        use Variables, only: SWP_min_vol, Sn_star, Sn, per_vol, ASW, SWP, &
                             fSWP, SMD, AEt, Et, Es, PEt, Ei

        Ei_dd = 0
        PEt_dd = 0
        Et_dd = 0
        Es_dd = 0
        Ei = 0
        PEt = 0
        Et = 0
        Es = 0
        AEt = 0

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
    end subroutine Init_SoilWater

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
                             Rsto_PEt, Sn, Rinc, Rgs
        use Params_Site, only: Fc_m

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

    !
    ! The values for each component are the sum of the previous day's values
    !
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

    !
    ! Calculate soil water potential from the previous day's totals
    ! (Calc_Penman_Monteith_daily must be run first).
    !
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
    

end module SoilWater
