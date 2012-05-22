module DO3SE_resistance

    public :: do3se_Ra_simple
    public :: do3se_Rb

    private

contains

    ! =========================================================================
    ! Calculate aerodynamic resistance between two heights using the simple,
    ! neutral stability model.
    ! =========================================================================
    pure function do3se_Ra_simple(ustar, z1, z2, d) result (ra)
        real, intent(in) :: ustar   ! Friction velocity (m/s)
        real, intent(in) :: z1      ! Lower height (m)
        real, intent(in) :: z2      ! Upper height (m)
        real, intent(in) :: d       ! Zero displacement height (m)
        real :: ra                  ! Output: aerodynamic resistance (s/m)

        real, parameter :: K = 0.41 ! von Karman's constant

        ra = (1.0 / (ustar * K)) * log((z2 - d) / (z1 - d))
    end function do3se_Ra_simple


    ! =========================================================================
    ! Calculate the "quasi-laminar boundary layer resistance" based on a given
    ! friction velocity and diffusivity.
    ! =========================================================================
    pure function do3se_Rb(ustar, d) result (rb)
        real, intent(in)    :: ustar    ! Friction velocity (m/s)
        real, intent(in)    :: d        ! Molecular diffusivity of substance in air (m2/s)
        real                :: rb       ! Output: Rb (s/m)

        real, parameter     :: PR = 0.72    ! Prandtl number
        real, parameter     :: K = 0.41     ! von Karman's constant
        real, parameter     :: V = 0.000015 ! Kinematic viscosity of air at 20 C (m2/s)

        rb = (2.0 / (K * ustar)) * (((V/d)/PR)**(2.0/3.0))
    end function do3se_Rb

end module DO3SE_resistance