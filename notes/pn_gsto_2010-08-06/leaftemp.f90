module LeafTemp

    implicit none

    real, parameter :: R = 8.3144621    ! Universal gas constant, J mol-1 K-1
    real, parameter :: M_A = 29.0       ! Molecular weight of air, g mol-1
    real, parameter :: c_p = 1010.0     ! Specific heat capacity of dry air at
                                        !   standard pressure and 20 C, J kg-1 K-1

contains

    real function Tleaf (Tair, P, Rn, VPD, g_a, g_c)
        real, intent(in) :: Tair    ! Air temperature, degrees C
        real, intent(in) :: P       ! Atmospheric pressure, kPa
        real, intent(in) :: Rn      ! Net radiation, W m-2
        real, intent(in) :: VPD     ! Vapour pressure deficit, kPa
        real, intent(in) :: g_a     ! Aerodynamic resistance
        real, intent(in) :: g_c     ! Canopy resistance

        real :: rho, VDD, e_s, s, lambda, psychro, phi, g_w
        ! Density of dry air, kg m-3
        rho = (P * M_A) / (R * (Tair + 273.15))
        ! Vapour density deficit, kg m-3
        VDD = rho * 0.622 * VPD / P
        ! Saturation vapour pressure, kPa
        e_s = 0.611 * exp(17.27 * Tair / (Tair + 237.3))
        ! Slope of saturation VDD curve, kg m-3 K-1
        s = (4098.0 * rho * 0.622 * e_s) / (P * (Tair + 237.3)**2)
        ! Latent heat vapourisation of water, J kg-1
        lambda = (-0.0000614342*Tair**3 + 0.00158927*Tair**2 - 2.36418*Tair + 2500.79) * 1000
        ! Psychrometric parameter, kg m-3 K-1
        psychro = rho * c_p / lambda
        ! Energy balance, W m-2
        phi = Rn
        ! Combined resistance to water vapour
        g_w = 1.0 / ((1.0 / g_a) + (1.0 / g_c))
        ! Leaf temperature, degrees C
        Tleaf = Tair + ((phi - lambda * g_w * VDD) / (lambda * (s * g_w + psychro * g_a)))
    end function Tleaf

end module LeafTemp


program TestLeafTemp

    !implicit none

    use LeafTemp, only: Tleaf

    real :: Tair
    real :: P
    real :: Rn
    real :: VPD
    real :: g_a
    real :: g_c

    real, parameter :: zR = 3, h = 1.7, d = h * 0.7, zo = h * 0.1
    real, parameter :: k = 0.41
    real :: u, ustar, Ra, Tl

    do
        ! Read row of data
        read (*, *, iostat=ios) Tair, P, Rn , VPD, u, g_c

        ! Derive g_a
        ustar = (u * k) / log((zR - d) / zo)
        ustar = max(0.0001, ustar)
        Ra = (1 / (ustar * k)) * log((zR - d) / (h - d))
        g_a = 1.0 / Ra

        ! Replace g_a and g_c with some "normal" constants
        !g_a = 0.05
        !g_c = 0.025

        ! Output results
        Tl = Tleaf(Tair, P, Rn, VPD, g_a, g_c)
        write (*, *) u, Rn, Tair, Tl, Tl - Tair

        ! Stop if we reached the end of the file
        if (ios /= 0) exit
    end do

end program TestLeafTemp
