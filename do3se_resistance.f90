module DO3SE_resistance

    public :: GstoType
    public :: do3se_Ra_simple
    public :: do3se_Rb
    public :: do3se_multiplicative_gsto

    ! =========================================================================
    ! Stomatal conductance (Gsto)
    !
    ! This type encapsulates the different variations of stomatal conductance.
    ! All are in units of mmol O3 m-2 PLA s-1.
    !
    ! leaf:             mean Gsto of upper canopy leaf
    ! mean:             mean Gsto of whole canopy
    ! canopy:           total canopy Gsto, taking leaf area into account
    ! canopy_noSMD:     same as "canopy", but assuming no SWP influence
    ! =========================================================================
    type GstoType
        real :: leaf, mean, canopy, canopy_noSMD
    end type GstoType

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


    ! =========================================================================
    ! Calculate variations of stomatal conductance using the mulitplicative
    ! model.
    ! =========================================================================
    pure elemental function do3se_multiplicative_gsto(gmax, fmin, gmorph, LAI, &
            fphen, leaf_fphen, flight, leaf_flight, ftemp, fVPD, fSWP, fO3) result (gsto)
        real, intent(in)    :: gmax         ! Maximum gsto (mmol O3 m-2 PLA s-1)
        real, intent(in)    :: fmin         ! Minimum gsto fraction (fraction)
        real, intent(in)    :: gmorph       ! Sun/shade morphology factor (fraction)
        real, intent(in)    :: LAI          ! Leaf area index, for bulk gsto (m^2/m^2)

        real, intent(in)    :: fphen        ! Phenology-related effect on gsto (fraction)
        real, intent(in)    :: leaf_fphen   ! Phenology-related effect on leaf gsto (fraction)
        real, intent(in)    :: flight       ! Irradiance effect on gsto (fraction)
        real, intent(in)    :: leaf_flight  ! Irradiance effect on leaf gsto (fraction)
        real, intent(in)    :: ftemp        ! Temperature effect on gsto (fraction)
        real, intent(in)    :: fVPD         ! VPD effect on gsto (fraction)
        real, intent(in)    :: fSWP         ! Soil water effect on gsto (fraction)
        real, intent(in)    :: fO3          ! O3 effect on gsto (fraction)

        type(GstoType)      :: gsto         ! Output: stomatal conductances (mmol O3 m-2 PLA s-1)

        gsto%leaf = gmax * min(leaf_fphen, fO3) * leaf_flight * max(fmin, ftemp * fVPD * fSWP)
        gsto%mean = gmax * gmorph * fphen * flight * max(fmin, ftemp * fVPD * fSWP)
        gsto%canopy = gsto%mean * LAI
        gsto%canopy_noSMD = gmax * fphen * flight * ftemp * fVPD * LAI
    end function do3se_multiplicative_gsto

end module DO3SE_resistance
