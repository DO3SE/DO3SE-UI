module DO3SE_utils

    public :: deg2rad
    public :: do3se_vegetation_d_and_z0
    public :: do3se_LAI_sunlit_fraction

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
    ! fraction of the LAI which is sunlit.
    ! =========================================================================
    pure function do3se_LAI_sunlit_fraction(LAI, sinB) result (LAIsunfrac)
        real, intent(in)    :: LAI          ! Leaf area index (m^2/m^2)
        real, intent(in)    :: sinB         ! sin(B), B = solar elevation angle
        real                :: LAIsunfrac   ! Output: fraction of LAI that is sunlit

        LAIsunfrac = ((1 - exp(-0.5 * LAI / sinB)) * (2 * sinB)) / LAI
    end function do3se_LAI_sunlit_fraction

end module DO3SE_utils