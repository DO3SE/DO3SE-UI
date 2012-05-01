module Functions

    public :: deg2rad

contains

    pure function deg2rad(x) result (retval)
        real, intent(in)    :: x        ! Angle in degrees
        real                :: retval   ! Output: angle in radians

        real, parameter :: D2R = 0.017453292519943295

        retval = x * D2R
    end function deg2rad

end module Functions
