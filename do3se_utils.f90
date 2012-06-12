module DO3SE_utils

    public :: deg2rad
    public :: do3se_vegetation_d_and_z0
    public :: do3se_sunlit_LAI
    public :: do3se_rsto_from_gsto

    private

contains

    ! =========================================================================
    ! Convert degrees to radians
    ! =========================================================================
    pure function deg2rad(x) result (retval)
        real, intent(in)    :: x        ! Angle in degrees
        real                :: retval   ! Output: angle in radians

        real, parameter :: D2R = 0.017453292519943295

        retval = x * D2R
    end function deg2rad


    ! =========================================================================
    ! Esimate "displacement height" and "roughness length" for the log wind
    ! profile from a vegetation height.
    ! =========================================================================
    pure subroutine do3se_vegetation_d_and_z0(h, d, z0)
        real, intent(in)    :: h    ! Vegetation height (m)
        real, intent(out)   :: d    ! Displacement height (m)
        real, intent(out)   :: z0   ! Roughness length (m)

        d = 0.7 * h
        z0 = 0.1 * h
    end subroutine do3se_vegetation_d_and_z0


    ! =========================================================================
    ! For a given solar elevation angle and leaf area index, calculate the
    ! the sunlit LAI from the total LAI.
    ! =========================================================================
    pure elemental function do3se_sunlit_LAI(LAI, sinB) result (sunLAI)
        real, intent(in)    :: LAI          ! Leaf area index (m^2/m^2)
        real, intent(in)    :: sinB         ! sin(B), B = solar elevation angle
        real                :: sunLAI       ! Output: sunlit LAI (m^2/m^2)

        sunLAI = ((1 - exp(-0.5 * LAI / sinB)) * (2 * sinB))
    end function do3se_sunlit_LAI


    ! =========================================================================
    ! Convert stomatal conductance to stomatal resistance, including all the
    ! unit conversions from mmol m-2 s-1 to s m-1.
    !
    ! The maximum stomatal resistance is capped to prevent infinite values when
    ! the conductance is 0.
    ! =========================================================================
    pure function do3se_rsto_from_gsto(gsto) result (rsto)
        real, intent(in)    :: gsto     ! Stomatal conductance (mmol m-2 s-1)
        real                :: rsto     ! Output: stomatal resistance (s m-1)
        real, parameter :: MAX_RSTO = 100000

        if (gsto <= 0) then
            rsto = MAX_RSTO
        else
            ! (gsto in m s-1) = 41000 * (gsto in mmol m-2 s-1)
            ! (rsto in s m-1) = 1 / (gsto in m s-1)
            rsto = 41000.0 / gsto
        end if
    end function do3se_rsto_from_gsto

end module DO3SE_utils
