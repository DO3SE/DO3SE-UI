module Irradiance

    public :: Calc_Flight

contains

    subroutine Calc_Flight()
        use Constants, only: DEG2RAD, PARfrac, Wm2_2uEPAR
        use Inputs, only: Idrctt, Idfuse, zen
        use Params_Veg, only: f_lightfac, cosA, albedo
        use Variables, only: LAI, LAIsunfrac, PARshade, PARsun, &
            leaf_flight, Flight

        real*8 :: sunLAI  ! sunlit LAI
        real*8 :: sinB    ! B = solar elevation angle component of zenith angle
        real*8 :: f_shade ! shade-leaf contribution to flight

        if ( zen <= 88 .and. LAI > 0 ) then
            sinB = cos(zen * DEG2RAD)   ! uses EMEP output zen to estimate sinB
                                        ! ensures consistency between zen and 
                                        ! Idrctt and Idfuse

            sunLAI = (1.0 - exp(-0.5*LAI/sinB)) * sinB/cosA
            LAIsunfrac = sunLAI / LAI

            ! PAR flux densities evaluated using method of Norman (1982, p.79):
            ! "conceptually, 0.07 represents a scattering coefficient"
            PARshade = Idfuse * exp(-0.5*LAI**0.7) + 0.07 * Idrctt * (1.1 - 0.1*LAI)*exp(-sinB)
            PARsun = Idrctt * cosA/sinB + PARshade

            ! Convert units, to PAR fraction, and multiply by albedo
            PARshade = PARshade * Wm2_2uEPAR * ( 1.0 - albedo )
            PARsun   = PARsun   * Wm2_2uEPAR * ( 1.0 - albedo )
        else
            LAIsunfrac = 0
            PARshade = 0
            PARsun = 0
        end if

        ! Calculate Flight and leaf_flight
        leaf_flight = (1.0 - exp(-f_lightfac*PARsun))
        f_shade     = (1.0 - exp(-f_lightfac*PARshade))
        Flight      = LAIsunfrac * leaf_flight + (1.0 - LAIsunfrac) * f_shade
    end subroutine Calc_Flight

end module Irradiance
