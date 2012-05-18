!
! Soil water calculations
!
! Terminology:
!   Fc_m    = Volumetric field capacity
!   Sn_star = Initial volumetric water content, <= Fc_m
!   Sn      = Current volumetric water content, <= Fc_m
!   P_input = Preciptation input (after evaporation of intercepted)
!   Sn_diff = Today's volumetric water content change (+ve = gain)
!   ASW     = Available soil water (m), = Sn - PWP_vol
!   SWP     = Soil water potential (MPa)
!   per_vol = Volumetric water content as a percentage
!   SMD     = Soil moisture deficit (m), relative to field capacity
!   PWP     = Minimum SWP (MPa)
!   PWP_vol = Minimum SWP as volumetric content (m3/m3)
!
module SoilWater

    public :: Init_SoilWater
    public :: Calc_Penman_Monteith
    public :: Calc_Penman_Monteith_daily
    public :: Calc_SWP
    public :: Calc_fSWP_exponential
    public :: Calc_fSWP_linear
    public :: Calc_LWP
    public :: Calc_LWP_steady_state
    public :: Calc_fLWP
    public :: Calc_SWP_meas
    public :: Calc_fPAW
    public :: fSWP_exp_curve

    ! Constants
    ! TODO: remove these
    real, public, parameter :: ASW_min = 0.0    ! ASW for min g (% of ASW_FC)
    real, public, parameter :: ASW_max = 50.0   ! ASW for max g (% of ASW_FC)

    ! Calculated constants
    real, public :: ASW_FC

    ! Hourly intermediate
    real, public :: Ei_hr
    real, public :: Es_hr
    real, public :: PEt_hr
    real, public :: Et_hr
    real, public :: Et_hr_prev
    real, public :: PEt_3
    real, public :: Et_3
    real, public :: AEt_hr

    ! Daily accumulation variables
    real, private :: Ei_dd, PEt_dd, Et_dd, Es_dd, AEt_dd

    real, private :: PWP, PWP_vol

    real, private :: r_meas

contains

    ! =======================================================================
    ! Calculate the change in volumetric water content due to precipitation
    ! and evapotranspiration.
    ! =======================================================================
    pure function do3se_Sn_diff(precip, LAI, Ei, AEt, root) result(Sn_diff)
        real, intent(in)    :: precip   ! Day's precipitation (m)
        real, intent(in)    :: LAI      ! Leaf area index (m^2/m^2)
        real, intent(in)    :: Ei       ! Day's evaporation of intercepted precipitation
        real, intent(in)    :: AEt      ! Day's evapotranspiration from plant and soil (m)
        real, intent(in)    :: root     ! Root depth (m)
        real                :: Sn_diff  ! Output: change in volumetric water content (m^3/m^3)

        real :: P_input

        ! Estimate precipitation that recharges the soil water
        ! The first (0.0001*LAI) of precipitation is assumed to be intercepted, and then
        ! the evaporation (Ei) is applied to this amount.  Soil water cannot be lost through Ei.
        if (precip > 0) then
            P_input = (precip - (0.0001*LAI)) + max(0.0, (0.0001*LAI) - Ei)
            P_input = max(0.0, P_input)
        else
            P_input = 0
        end if

        ! Total water change = incoming not evaporated - evapotranspiration from plant and soil
        ! Converted to volumetric change using root depth
        Sn_diff = (P_input - AEt) / root
    end function do3se_Sn_diff
    
    subroutine Init_SoilWater()
        use Constants, only: SWC_sat
        use Parameters, only: Fc_m, soil_b, SWP_AE, D_meas
        use Parameters, only: SWP_min, SWP_max, fmin, root
        use Variables, only: Sn_star, Sn, per_vol, ASW, SWP, &
                             fSWP, SMD, AEt, Et, Es, PEt, Ei, fLWP, &
                             Sn_meas, SWP_meas, SMD_meas

        Ei_dd = 0
        PEt_dd = 0
        Et_dd = 0
        Es_dd = 0
        AEt_dd = 0
        Ei = 0
        PEt = 0
        Et = 0
        Es = 0
        AEt = 0

        ! PWP can't be any higher than SWP_min
        PWP = min(-4.0, SWP_min)
        ! Convert PWP to volumetric (MPa -> m^3/m^3)
        PWP_vol = 1.0 / (((PWP/SWP_AE)**(1.0/soil_b)) / SWC_sat)

        ! Volumetric water content, initially at field capacity
        Sn_star = Fc_m
        Sn = Sn_star

        ! As a percentage
        per_vol = Sn * 100

        ! ASW and SWP for initial volumetric water content
        ASW = (Sn - PWP_vol) * root
        ASW_FC = (Fc_m - PWP_vol) * root
        SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

        ! Calculate fSWP and SMD for initial water content
        fSWP = fSWP_exp_curve(SWP, fmin)
        SMD = (Fc_m - Sn) * root

        ! Initial fLWP = 1
        fLWP = 1

        ! Initialised SWP_meas
        r_meas = (1-(0.97**(D_meas*100)))
        Sn_meas = Sn_star
        SWP_meas = SWP_AE*((SWC_sat/Sn_meas)**soil_b)
    end subroutine Init_SoilWater

    !
    ! Calculate the evaporation of intercepted precipitation (Ei), potential
    ! plant transpiration (PEt), actual plant transpiration (Et), actual
    ! evapotranspiration (AEt) and soil evaporation (Es) using the
    ! Penman-Monteith method.
    !
    subroutine Calc_Penman_Monteith()
        use Constants, only: seaP, Ts_K, Dratio
        use Inputs, only: VPD, Ts_C, P, dd, Rn_MJ => Rn, esat_kPa => esat, eact_kPa => eact
        use Variables, only: Ei, Et, PEt, AEt, Es, Rb_H2O, LAI, Rsto_c, &
                             Rsto_PEt, Sn, Ra, Rinc, Es_blocked
        use Parameters, only: Fc_m, Rsoil

        real        :: VPD_Pa       ! VPD in Pa, not kPa
        real        :: P_Pa         ! Pressure in Pa, not kPa
        real        :: esat, eact   ! esat and eact in Pa
        real        :: Tvir, delta, lambda, psychro, Pair, Cair, G
        
        real        :: Et_1, Et_2, Ei_3 !, PEt_3, Et_3, Ei_hr, PEt_hr, Et_hr
        real        :: t, Es_Rn, Es_G, Es_1, Es_2, Es_3 !, Es_hr
        real :: SW_a, SW_s, SW_c, C_canopy, C_soil

        ! Convert Rn to J from MJ
        real :: Rn
        Rn = Rn_MJ * 1000000.0

        VPD_Pa = VPD * 1000
        P_Pa = P * 1000

        esat = 1000 * esat_kPa
        eact = 1000 * eact_kPa

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

        PEt_3 = delta + psychro * (1 + (Rsto_PEt * Dratio) / Rb_H2O)
        PEt_hr = (Et_1 + Et_2) / PEt_3 / 1000

        Et_3 = delta + psychro * (1 + (Rsto_c * Dratio) / Rb_H2O)
        Et_hr_prev = Et_hr
        Et_hr = (Et_1 + Et_2) / Et_3 / 1000

        if (Es_blocked) then
            Es_hr = 0
        else
            t = exp(-0.5 * LAI)
            Es_Rn = Rn * t
            Es_G = 0.1 * Es_Rn
            Es_1 = (delta * (Rn - G)) / lambda
            Es_2 = ((3600 * Pair * Cair * VPD_Pa) - (delta * Rinc * ((Rn - G) - (Es_Rn - Es_G)))) / (Rinc + Rb_H2O) / lambda
            Es_3 = delta + (psychro * (1.0 + (Rsoil / (Rb_H2O + Rinc))))
            Es_hr = (Es_1 + Es_2) / Es_3 / 1000
        endif

        ! Calculate AEt from Et and Es (after Shuttleworth and Wallace, 1985)
        SW_a = (delta + psychro) * (Ra + Rb_H2O)
        SW_s = (delta + psychro) * Rinc + (psychro * Rsoil)
        SW_c = (delta + psychro) * 0 + (psychro + Rsto_c) ! Boundary layer 
                                                          ! resistance = 0
        C_canopy = 1 / (1 + ((SW_c * SW_a) / (SW_s * (SW_c + SW_a))))
        C_soil = 1 / (1 + ((SW_s * SW_a) / (SW_c * (SW_s + SW_a))))
        if (Es_hr <= 0) then
            AEt_hr = Et_hr
        else
            AEt_hr = (C_canopy * Et_hr) + (C_soil * Es_hr)
        end if

        Ei_dd = Ei_dd + Ei_hr
        PEt_dd = PEt_dd + PEt_hr
        Et_dd = Et_dd + Et_hr
        Es_dd = Es_dd + Es_hr
        AEt_dd = AEt_dd + AEt_hr
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
        AEt = AEt_dd
        AEt_dd = 0
    end subroutine Calc_Penman_Monteith_daily

    !
    ! Calculate soil water potential from the previous day's totals
    ! (Calc_Penman_Monteith_daily must be run first).
    !
    subroutine Calc_SWP()
        use Constants, only: SWC_sat
        use Parameters, only: Fc_m, soil_b, SWP_AE
        use Parameters, only: SWP_min, SWP_max, fmin, root
        use Inputs, only: dd, precip_acc
        use Variables, only: AEt, Es, Ei, LAI
        use Variables, only: Sn, per_vol, ASW, SWP, fSWP, SMD
        use Variables, only: Sn_diff

        Sn_diff = do3se_Sn_diff(precip_acc, LAI, Ei, AEt, root)

        ! Calculate new Sn, with field capacity as a maximum
        Sn = min(Fc_m, Sn + Sn_diff)
        Sn = max(PWP_vol, Sn)
        per_vol = Sn * 100

        ! Calculate ASW and SWP for new water content
        ASW = (Sn - PWP_vol) * root
        SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

        ! Calculate SMD for new water content
        SMD = (Fc_m - Sn) * root
    end subroutine Calc_SWP

    subroutine Calc_fSWP_exponential()
        use Parameters, only: fmin
        use Variables, only: SWP, fSWP

        fSWP = fSWP_exp_curve(SWP, fmin)
    end subroutine Calc_fSWP_exponential

    subroutine Calc_fSWP_linear()
        use Parameters, only: fmin, SWP_min, SWP_max
        use Variables, only: fSWP, SWP

        fSWP = min(1.0, max(fmin, ((1-fmin) * ((SWP_min - SWP)/(SWP_min - SWP_max))) + fmin))
    end subroutine Calc_fSWP_linear

    subroutine Calc_LWP()
        use Parameters, only: root, fmin
        use Parameters, only: SWP_AE, soil_b, Ksat
        use Variables, only: SWP, delta_LWP, LWP, fLWP
        use Inputs, only: hr

        ! Variables related to plant physiology
        ! TODO: These should probably be vegetation parameters
        real :: K1 = 0.0000000000035    ! constant related to root density
        real :: C = 1                   ! plant capacitance (MPa mm-1)
        real :: Rc = 0.43               ! storage/destorage hydraulic resistance
                                        ! (MPa h mm-1)
        real :: Rp = 5.3                ! plant hydraulic resistance (MPa h mm-1)

        ! Calculated LWP parameters
        real :: Rsr         ! Soil-rot resistance
        real :: Ks          ! Bulk soil hydraulic conductivity
        real :: delta_t     ! Time between readings - TODO: handle when readings 
                            ! are NOT hourly?
        real :: delta_Et    ! Difference in hourly Et from last hour

        Ks = Ksat * ((SWP_AE/SWP)**((3/soil_b)+2))
        Rsr = K1 / (root * Ks)

        delta_t = 1
        delta_Et = Et_hr_prev - Et_hr

        if (hr < 3) then
            delta_LWP = 0
            LWP = SWP
        else
            delta_LWP = ((((SWP-LWP-(Rsr+Rp)*(Et_hr_prev*1000))/(C*(Rsr+Rp+Rc)))*Delta_t) &
                         -(((Rsr+Rp)*Rc)/(Rsr+Rp+Rc))*(delta_Et*1000))
            LWP = LWP + delta_LWP
        end if
    end subroutine Calc_LWP

    subroutine Calc_LWP_steady_state()
        use Parameters, only: SWP_AE, soil_b, Ksat
        use Parameters, only: root
        use Variables, only: LWP, SWP

        ! Variables related to plant physiology
        ! TODO: These should probably be vegetation parameters
        real :: K1 = 0.0000000000035    ! constant related to root density
        real :: C = 1                   ! plant capacitance (MPa mm-1)
        real :: Rc = 0.43               ! storage/destorage hydraulic resistance
                                        ! (MPa h mm-1)
        real :: Rp = 5.3                ! plant hydraulic resistance (MPa h mm-1)

        ! Calculated LWP parameters
        real :: Rsr         ! Soil-rot resistance
        real :: Ks          ! Bulk soil hydraulic conductivity

        Ks = Ksat * ((SWP_AE/SWP)**((3/soil_b)+2))
        Rsr = K1 / (root * Ks)

        LWP = SWP - (Et_hr*1000 * (Rsr + Rp))
    end subroutine Calc_LWP_steady_state

    subroutine Calc_fLWP()
        use Parameters, only: fmin
        use Variables, only: LWP, fLWP

        fLWP = fSWP_exp_curve(LWP, fmin)
    end subroutine Calc_fLWP

    subroutine Calc_SWP_meas()
        use Inputs, only: precip_acc
        use Constants, only: SWC_sat
        use Variables, only: AEt, Ei, LAI, Sn_meas, Sn_diff_meas, SWP_meas, &
                             SMD_meas
        use Parameters, only: Fc_m, soil_b, SWP_AE, D_meas

        real :: Et_meas

        Et_meas = AEt * r_meas
        Sn_diff_meas = do3se_Sn_diff(precip_acc, LAI, Ei, Et_meas, D_meas)
        
        Sn_meas = min(Fc_m, Sn_meas + Sn_diff_meas)
        Sn_meas = max(PWP_vol, Sn_meas)
        
        SWP_meas = SWP_AE * ((SWC_sat / Sn_meas)**soil_b)

        SMD_meas = (Fc_m - Sn_meas) * D_meas
    end subroutine Calc_SWP_meas


    ! =======================================================================
    ! Calculate fPAW based on available soil water
    !
    ! Marked as elemental, most useful for calculating fPAW based on more
    ! than one fmin.
    ! =======================================================================
    pure elemental function do3se_fPAW(ASW, ASW_FC, fmin) result (fPAW)
        real, intent(in) :: ASW         ! Available soil water (m)
        real, intent(in) :: ASW_FC      ! Available soil water when at field capacity (m)
        real, intent(in) :: fmin        ! Minimum gsto fraction (fraction)
        real :: fPAW                    ! Output: fPAW

        real, parameter :: ASW_min = 0.0    ! ASW for min g (% of ASW_FC)
        real, parameter :: ASW_max = 50.0   ! ASW for max g (% of ASW_FC)

        fPAW = fmin + (1.0 - fmin) * ((100 * (ASW/ASW_FC)) - ASW_min) / (ASW_max - ASW_min)
        fPAW = max(fmin, min(1.0, fPAW))
    end function do3se_fPAW
    
    subroutine Calc_fPAW()
        use Variables, only: ASW, fPAW
        use Parameters, only: fmin

        fPAW = do3se_fPAW(ASW, ASW_FC, fmin)
    end subroutine Calc_fPAW

    function fSWP_exp_curve(SWP, fmin) result(fSWP)
        real, intent(in) :: SWP, fmin
        real :: fSWP

        fSWP = (((-1) * SWP)** (-0.706)) * 0.355
        fSWP = min(max(fSWP, fmin), 1.0)
    end function fSWP_exp_curve

end module SoilWater
