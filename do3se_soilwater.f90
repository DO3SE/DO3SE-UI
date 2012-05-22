module DO3SE_soilwater

    public :: do3se_Sn_diff
    public :: do3se_SMD
    public :: do3se_f_PAW

    private

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


    ! =======================================================================
    ! Calculate the various measures of soil moisture: volumetric water
    ! content, available soil water, soil water potential and soil moisture
    ! deficit.
    ! =======================================================================
    pure subroutine do3se_SMD(Sn_diff, Sn_old, root, Fc_m, SWP_AE, soil_b, SWP_min, &
                              Sn, per_vol, ASW, SWP, SMD)
        real, intent(in) :: Sn_diff     ! Change in volumetric water content (m^3/m^3)
        real, intent(in) :: Sn_old      ! Previous day's volumetric water content (m3/m3)
        real, intent(in) :: root        ! Root depth (m)
        real, intent(in) :: Fc_m        ! Volumetric field capacity (m3/m3)
        real, intent(in) :: SWP_AE      ! Soil water potential at air entry (MPa)
        real, intent(in) :: soil_b      ! SWC constant b
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
        PWP_vol = 1.0 / (((PWP/SWP_AE)**(1.0/soil_b)) / SWC_sat)

        ! Calculate new volumetric water content, Sn (m3/m3), with field capacity as maximum,
        ! and "permanent wilting point" as minimum.
        Sn = max(PWP_vol, min(Fc_m, Sn_old + Sn_diff))
        ! Water content as percentage
        per_vol = Sn * 100

        ! Calculate available soil water (ASW) and soil water potential (SWP)
        ASW = (Sn - PWP_vol) * root
        SWP = SWP_AE * ((SWC_sat / Sn)**soil_b)

        ! Calculate SMD for new water content
        SMD = (Fc_m - Sn) * root
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