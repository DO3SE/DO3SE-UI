module leaftemp_jackson


contains

    real function Tleaf (Tair, P, VPD, Rn, ra, rc)
        implicit none

        real, intent(in) :: Tair    ! Ambient temperature (C)
        real, intent(in) :: P       ! Air pressure (Pa)
        real, intent(in) :: VPD     ! Vapour pressure deficit (Pa)
        real, intent(in) :: Rn      ! Net radiation (W m-2)
        real, intent(in) :: ra      ! Aerodynamic resistance (s m-1)
        real, intent(in) :: rc      ! Canopy resistance (s m-1)

        real, parameter :: c_p = 1010.0     ! Specific heat capacity of dry air at 
                                            !   standard pressure and 20C, J kg-1 C-1

        real :: esat, eact, Tvir, rho, delta, lambda, psychro, Tdiff_1, Tdiff

        ! Saturation vapour pressure at Tair (Pa)
        esat = 611 * exp(17.27 * Tair / (Tair + 237.3))
        ! Actual vapour pressure (Pa)
        eact = esat - VPD
        ! Virtual temperature for density calcualation (K)
        Tvir = (Tair + 273.15) / (1 - (0.378 * (eact / P)))
        ! Density of air (kg m-3)
        rho = P / (287.058 * Tvir)
        ! Slope of saturation vapour pressure curve (Pa C-1)
        delta = (4098 * esat) / ((Tair + 237.3)**2)
        ! Latent heat vapourisation of water (J kg-1)
        lambda = (-0.0000614342*Tair**3 + 0.00158927*Tair**2 - 2.36418*Tair + 2500.79) * 1000
        ! Psychrometric parameter (Pa C-1)
        psychro = 1628.6 * P / lambda

        ! Leaf - air temperature difference (C)
        Tdiff_1 = psychro * (1 + (rc / ra))
        Tdiff = ((ra * Rn) / (rho * c_p)) * (Tdiff_1 / (delta + Tdiff_1)) - (VPD / (delta + Tdiff_1))
        ! Leaf temperature (C)
        Tleaf = Tair + Tdiff
    end function Tleaf

end module leaftemp_jackson


program test_leaftemp_jackson

    use leaftemp_jackson, only: Tleaf

    real :: Tair, P, VPD, ra, rc
    real :: Tl
    integer :: ios

    do
        read (*, *, iostat=ios) Tair, P, VPD, Rn, ra, rc
        Tl = Tleaf(Tair, P * 1000, VPD * 1000, Rn, ra, rc)
        write (*, *) Tair, Tl, Tl - Tair, P, VPD, Rn, ra, rc
        if (ios /= 0) exit
    end do

end program test_leaftemp_jackson
