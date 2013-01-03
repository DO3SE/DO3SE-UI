module DO3SE_env

    public :: do3se_f_VPD_linear
    public :: do3se_f_VPD_simple_log
    public :: do3se_f_temp
    public :: do3se_f_temp_no_drop
    public :: do3se_f_light

    private

contains
    
    ! =========================================================================
    ! Calculate VPD effect on gsto, fVPD.
    !
    ! Note that VPD_min and VPD_max refer to the value for min. and max.
    ! gsto, therefore VPD_min should be greater than VPD_max.
    !
    ! Marked elemental so fVPD can be calculated for multiple
    ! parametrisations simultaneously.
    ! =========================================================================
    pure elemental function do3se_f_VPD_linear(VPD, VPD_min, VPD_max, fmin) result (fVPD)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (kPa)
        real, intent(in)    :: VPD_min  ! VPD for minimum gsto (kPa)
        real, intent(in)    :: VPD_max  ! VPD for maximum gsto (kPa)
        real, intent(in)    :: fmin     ! Minimum fVPD
        real                :: fVPD     ! Output: VPD effect on gsto

        fVPD = ((1 - fmin) * (VPD_min - VPD)/(VPD_min - VPD_max)) + fmin
        fVPD = max(fmin, min(1.0, fVPD))
    end function do3se_f_VPD_linear


    ! =========================================================================
    ! Calculate VPD effect on gsto, fVPD, using a simplified logarithmic
    ! relationship.
    ! =========================================================================
    pure elemental function do3se_f_VPD_simple_log(VPD, fmin) result (fVPD)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (kPa)
        real, intent(in)    :: fmin     ! Minimum fVPD
        real                :: fVPD     ! Output: VPD effect on gsto

        fVPD = 1.0 - 0.6 * log(VPD)
        fVPD = max(fmin, min(1.0, fVPD))
    end function do3se_f_VPD_simple_log


    ! =========================================================================
    ! Calculate temperature effect on gsto, ftemp
    !
    ! Marked as elemental so ftemp can be calculated for multiple
    ! parametrisations simultaneously.
    ! =========================================================================
    pure elemental function do3se_f_temp(Ts_C, T_min, T_opt, T_max, fmin) result (ftemp)
        real, intent(in)    :: Ts_C     ! Air temperature (degrees C)
        real, intent(in)    :: T_min    ! Minimum temperature (degrees C)
        real, intent(in)    :: T_opt    ! Temperature for maximum g (degrees C)
        real, intent(in)    :: T_max    ! Maximum temperature (degrees C)
        real, intent(in)    :: fmin     ! Minimum ftemp
        real                :: ftemp    ! Output: temperature effect on gsto

        real :: bt

        bt = (T_max - T_opt) / (T_opt - T_min)
        ftemp = ((Ts_C - T_min) / (T_opt - T_min)) * ((T_max - Ts_C) / (T_max - T_opt))**bt
        ftemp = max(fmin, min(1.0, ftemp))
    end function do3se_f_temp


    ! =========================================================================
    ! Calculate temperature effect on gsto, ftemp, with modified model.
    !
    ! The ftemp is calculated the same as with do3se_f_temp only when Ts_C is
    ! below T_opt.  The right half of the function is a constant 1 followed by
    ! an instantaneous drop to 0.
    ! =========================================================================
    pure elemental function do3se_f_temp_no_drop(Ts_C, T_min, T_opt, T_max, fmin) result (ftemp)
        real, intent(in)    :: Ts_C     ! Air temperature (degrees C)
        real, intent(in)    :: T_min    ! Minimum temperature (degrees C)
        real, intent(in)    :: T_opt    ! Temperature for maximum g (degrees C)
        real, intent(in)    :: T_max    ! Maximum temperature (degrees C)
        real, intent(in)    :: fmin     ! Minimum ftemp
        real                :: ftemp    ! Output: temperature effect on gsto

        if (Ts_C > T_max) then
            ftemp = 0.0
        else if (Ts_C > T_opt) then
            ftemp = 1.0
        else
            ftemp = do3se_f_temp(Ts_C, T_min, T_opt, T_max, fmin)
        end if
    end function do3se_f_temp_no_drop


    ! =========================================================================
    ! Calculate PAR irradiance effect on gsto, flight.
    !
    ! Marked as elemental so flight can be calculated for multiple
    ! parametrisations simultaneously.
    ! =========================================================================
    pure elemental subroutine do3se_f_light(Idrctt, Idfuse, sinB, LAI, LAIsunfrac, f_lightfac, cosA, &
                                            Flight, leaf_flight)
        real, intent(in)    :: Idrctt       ! Direct PAR irradiance (W m-2)
        real, intent(in)    :: Idfuse       ! Diffuse PAR irradiance (W m-2)
        real, intent(in)    :: sinB         ! sin(B), B = solar elevation angle
        real, intent(in)    :: LAI          ! Leaf area index (m^2/m^2)
        real, intent(in)    :: LAIsunfrac   ! Fraction of LAI that is sunlit
        real, intent(in)    :: f_lightfac   ! Single leaf Flight coefficient
        real, intent(in)    :: cosA         ! cos(A), A = mean leaf inclination
        real, intent(out)   :: Flight       ! Output: irradiance effect on whole-canopy gsto
        real, intent(out)   :: leaf_flight  ! Output: irradiance effect on leaf gsto

        real, parameter :: Wm2_uE = 4.57    ! Conversion from W m-2 to umol m-2 s-1

        real :: PARshade, PARsun, PPFDshade, PPFDsun, Flightsun, Flightshade

        if (sinB > 0 .and. LAI > 0) then
            ! PAR flux densities evaluated using method of Norman (1982, p.79):
            ! "conceptually, 0.07 represents a scattering coefficient"
            PARshade = Idfuse * exp(-0.5 * LAI**0.8) + &
                       0.07 * Idrctt * (1.1 - (0.1 * LAI)) * exp(-sinB)
            PARsun = Idrctt * 0.8 * (cosA / sinB) + PARshade

            ! Convert from W m-2 PAR to PPFD
            PPFDshade = PARshade * Wm2_uE
            PPFDsun = PARsun * Wm2_uE

            ! TODO: does this need albedo?
            Flightsun = (1.0 - exp(-f_lightfac * PPFDsun))
            Flightshade = (1.0 - exp(-f_lightfac * PPFDshade))

            ! TODO: "grassland multilayer" model used leaf_flight = Flightsun - 
            !       which version is right?
            leaf_flight = 1.0 - exp(-f_lightfac * ((Idrctt + Idfuse) * Wm2_uE))
            Flight = LAIsunfrac * Flightsun + (1.0 - LAIsunfrac) * Flightshade
        else
            leaf_flight = 0
            Flight = 0
        end if
    end subroutine do3se_f_light

end module DO3SE_env
