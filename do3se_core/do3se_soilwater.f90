module DO3SE_soilwater

    public :: SoilType

    public :: do3se_penman_monteith_hourly
    public :: do3se_Sn_diff
    public :: do3se_SMD
    public :: do3se_f_PAW

    ! SMD soil texture parameters
    type SoilType
        ! SWC constant b
        real :: soil_b
        ! Field capacity (m3/m3)
        real :: Fc_m
        ! Water potential at air entry (MPa)
        real :: SWP_AE
        ! Saturated soil conductance (s-2 MPa-1 mm-1)
        real :: Ksat
    end type SoilType

    private

contains

    ! =======================================================================
    ! Calculate the evaporation of intercepted precipitation (Ei), potential
    ! plant transpiration (PEt), actual plant transpiration (Et), actual
    ! evapotranspiration (AEt) and soil evaporation (Es) using the
    ! Penman-Monteith method.
    ! =======================================================================
    pure subroutine do3se_penman_monteith_hourly(Rn, VPD_Pa, P_Pa, Ts_C, LAI, &
                                                 Rsto_c, Rsto_PEt, Ra, Rb_H2O, &
                                                 Rinc, Rsoil, Es_blocked, &
                                                 Ei_hr, PEt_hr, Et_hr, Es_hr, AEt_hr)
        real, intent(in) :: Rn              ! Net radiation (J)
        real, intent(in) :: VPD_Pa          ! Vapour pressure deficit (Pa)
        real, intent(in) :: P_Pa            ! Atmospheric pressure (Pa)
        real, intent(in) :: Ts_C            ! Air temperature (degrees C)
        real, intent(in) :: LAI             ! Leaf area index (m2/m2)
        real, intent(in) :: Rsto_c          ! Canopy stomatal resistance (s/m)
        real, intent(in) :: Rsto_PEt        ! Canopy stomatal resistance without SMD influence (s/m)
        real, intent(in) :: Ra              ! Aerodynamic resistance (s/m)
        real, intent(in) :: Rb_H2O          ! Boundary layer resistance to water vapour (s/m)
        real, intent(in) :: Rinc            ! In-canopy resistance (s/m)
        real, intent(in) :: Rsoil           ! Soil resistance (s/m)
        logical, intent(in) :: Es_blocked   ! Is soil evaporation blocked?
        real, intent(out) :: Ei_hr          ! Output: hourly evaporation of intercepted precipitation (m/hour)
        real, intent(out) :: PEt_hr         ! Output: hourly potential transpiration assuming non-limiting SMD (m/hour)
        real, intent(out) :: Et_hr          ! Output: hourly plant transpiration (m/hour)
        real, intent(out) :: Es_hr          ! Output: hourly evaporation from soil (m/hour)
        real, intent(out) :: AEt_hr         ! Output: hourly evapotranspiration from plant and soil (m/hour)

        real, parameter :: Ts_K = 273.16    ! Conversion from degrees Celsius to Kelvin
        real, parameter :: Dratio = 0.662   ! Ratio between molecular diffusivity of O3 and H2O

        real :: esat, eact, Tvir, delta, lambda, psychro, Pair, Cair, G

        real :: Et_1, Et_2, Ei_3, PEt_3, Et_3
        real :: t, Es_Rn, Es_G, Es_1, Es_2, Es_3
        real :: SW_a, SW_s, SW_c, C_canopy, C_soil

        esat = 611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
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

        PEt_3 = delta + psychro * (1 + (Rsto_PEt * Dratio) / Rb_H2O)
        PEt_hr = (Et_1 + Et_2) / PEt_3 / 1000

        Et_3 = delta + psychro * (1 + (Rsto_c * Dratio) / Rb_H2O)
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
        end if

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
    end subroutine do3se_penman_monteith_hourly


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


    ! =======================================================================
    ! Calculate the various measures of soil moisture: volumetric water
    ! content, available soil water, soil water potential and soil moisture
    ! deficit.
    ! =======================================================================
    pure subroutine do3se_SMD(Sn_diff, Sn_old, root, soil, SWP_min, &
                              Sn, per_vol, ASW, SWP, SMD)
        real, intent(in) :: Sn_diff     ! Change in volumetric water content (m^3/m^3)
        real, intent(in) :: Sn_old      ! Previous day's volumetric water content (m3/m3)
        real, intent(in) :: root        ! Root depth (m)
        type(SoilType), intent(in) :: soil ! Soil texture parameters
        real, intent(in) :: SWP_min     ! SWP for min g (MPa)
        real, intent(out) :: Sn         ! Output: new volumetric water content (m3/m3)
        real, intent(out) :: per_vol    ! Output: Sn as percentage
        real, intent(out) :: ASW        ! Output: Available soil water (m)
        real, intent(out) :: SWP        ! Output: Soil water potential (MPa)
        real, intent(out) :: SMD        ! Output: Soil moisture deficit (m)

        real, parameter :: SWC_sat = 0.4 ! Saturated soil water content for soil water release curve

        real :: PWP, PWP_vol

        ! "Permanent wilting point", a minimum level for SWP.  Either -4.0 MPa or SWP_min,
        ! whichever is lower.
        PWP = min(-4.0, SWP_min)
        ! Convert to volumetric content to use for available soil water
        PWP_vol = 1.0 / (((PWP/soil%SWP_AE)**(1.0/soil%soil_b)) / SWC_sat)

        ! Calculate new volumetric water content, Sn (m3/m3), with field capacity as maximum,
        ! and "permanent wilting point" as minimum.
        Sn = max(PWP_vol, min(soil%Fc_m, Sn_old + Sn_diff))
        ! Water content as percentage
        per_vol = Sn * 100

        ! Calculate available soil water (ASW) and soil water potential (SWP)
        ASW = (Sn - PWP_vol) * root
        SWP = soil%SWP_AE * ((SWC_sat / Sn)**soil%soil_b)

        ! Calculate SMD for new water content
        SMD = (soil%Fc_m - Sn) * root
    end subroutine do3se_SMD


    ! =========================================================================
    ! Calculate fPAW based on available soil water
    !
    ! Marked as elemental, most useful for calculating fPAW based on more
    ! than one fmin.
    ! =========================================================================
    pure elemental function do3se_f_PAW(ASW, ASW_FC, fmin) result (fPAW)
        real, intent(in) :: ASW         ! Available soil water (m)
        real, intent(in) :: ASW_FC      ! Available soil water when at field capacity (m)
        real, intent(in) :: fmin        ! Minimum gsto fraction (fraction)
        real             :: fPAW        ! Output: fPAW

        real, parameter :: ASW_min = 0.0    ! ASW for min g (% of ASW_FC)
        real, parameter :: ASW_max = 50.0   ! ASW for max g (% of ASW_FC)

        fPAW = fmin + (1.0 - fmin) * ((100 * (ASW/ASW_FC)) - ASW_min) / (ASW_max - ASW_min)
        fPAW = max(fmin, min(1.0, fPAW))
    end function do3se_f_PAW

end module DO3SE_soilwater
