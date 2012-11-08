!
! Soil water calculations
!
! Terminology:
!   Fc_m    = Volumetric field capacity
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

contains
    
    subroutine Init_SoilWater()
        use Constants, only: SWC_sat
        use Parameters, only: soil, D_meas
        use Parameters, only: SWP_min, SWP_max, fmin, root
        use Variables, only: Sn, per_vol, ASW, SWP, &
                             fSWP, SMD, AEt, Et, Es, PEt, Ei, fLWP, &
                             Sn_meas, SWP_meas, SMD_meas

        use do3se_soilwater, only: do3se_SMD



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

        ! Calculate SMD variables as if soil water content is at its maximum
        ! (implicitly sets Sn = Fc_m)
        call do3se_SMD(0.0, soil%Fc_m, root, soil, SWP_min, &
                       Sn, per_vol, ASW, SWP, SMD)
        ! Need to store ASW at maximum soil water content
        ASW_FC = ASW

        ! TODO: allow initial soil water content to be set.  This will probably
        ! involve setting a new Sn and calling do3se_SMD() again.

        ! Calculate fSWP and SMD for initial water content
        fSWP = fSWP_exp_curve(SWP, fmin)
        ! Initial fLWP = 1
        fLWP = 1

        ! Initialise SWP_meas
        Sn_meas = soil%Fc_m
        call Calc_SWP_meas()
    end subroutine Init_SoilWater

    subroutine Calc_Penman_Monteith()
        use Inputs, only: VPD, Ts_C, P, Rn_MJ => Rn
        use Variables, only: Ra, Rb_H2O, Rsto_c, Rsto_PEt, Rinc, LAI, Es_blocked
        use Parameters, only: Rsoil

        use do3se_soilwater, only: do3se_penman_monteith_hourly

        ! Keep previous hour's Et_hr for LWP calculation
        Et_hr_prev = Et_hr

        call do3se_penman_monteith_hourly(Rn_MJ*1000000.0, VPD*1000.0, P*1000.0, Ts_C, LAI, &
                                          Rsto_c, Rsto_PEt, Ra, Rb_H2O, Rinc, Rsoil, Es_blocked, &
                                          Ei_hr, PEt_hr, Et_hr, Es_hr, AEt_hr)

        ! Accumulate daily changes for eventual Sn_diff calculation when the day is done
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
        use Parameters, only: soil
        use Parameters, only: SWP_min, SWP_max, fmin, root
        use Inputs, only: dd, precip_acc
        use Variables, only: AEt, Es, Ei, LAI
        use Variables, only: Sn, per_vol, ASW, SWP, fSWP, SMD
        use Variables, only: Sn_diff

        use do3se_soilwater, only: do3se_Sn_diff, do3se_SMD

        Sn_diff = do3se_Sn_diff(precip_acc, LAI, Ei, AEt, root)
        call do3se_SMD(Sn_diff, Sn, root, soil, SWP_min, &
                       Sn, per_vol, ASW, SWP, SMD)
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
        use Parameters, only: soil
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

        Ks = soil%Ksat * ((soil%SWP_AE/SWP)**((3/soil%soil_b)+2))
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
        use Parameters, only: soil
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

        Ks = soil%Ksat * ((soil%SWP_AE/SWP)**((3/soil%soil_b)+2))
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
        use Parameters, only: soil, D_meas, SWP_min

        use do3se_soilwater, only: do3se_Sn_diff, do3se_SMD

        real :: r_meas, Et_meas, ASW, per_vol

        r_meas = (1-(0.97**(D_meas*100)))
        Et_meas = AEt * r_meas
        Sn_diff_meas = do3se_Sn_diff(precip_acc, LAI, Ei, Et_meas, D_meas)

        call do3se_SMD(Sn_diff_meas, Sn_meas, D_meas, soil, SWP_min, &
                       Sn_meas, per_vol, ASW, SWP_meas, SMD_meas)
    end subroutine Calc_SWP_meas

    subroutine Calc_fPAW()
        use Variables, only: ASW, fPAW
        use Parameters, only: fmin

        use do3se_soilwater, only: do3se_f_PAW

        fPAW = do3se_f_PAW(ASW, ASW_FC, fmin)
    end subroutine Calc_fPAW

    function fSWP_exp_curve(SWP, fmin) result(fSWP)
        real, intent(in) :: SWP, fmin
        real :: fSWP

        fSWP = (((-1) * SWP)** (-0.706)) * 0.355
        fSWP = min(max(fSWP, fmin), 1.0)
    end function fSWP_exp_curve

end module SoilWater
