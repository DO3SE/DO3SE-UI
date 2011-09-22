module LeafTemp_Nobel

    implicit none

    real, parameter :: Kair = 0.0264    ! Thermal conductivity coefficient of 
                                        ! dry air at 30C (W m-1 C-1)

contains

    real function Tleaf (Tair, u, c, Lm, Jch)
        real, intent(in) :: Tair    ! Air temperature, degrees C
        real, intent(in) :: u       ! Wind speed, m/s
        real, intent(in) :: c       ! Boundary layer turbulence constant
        real, intent(in) :: Lm      ! Leaf dimension
        real, intent(in) :: Jch     ! Rate of heat conduction (W m-2)

        real :: bl      ! Boundary layer thickness (mm)
        real :: Tdiff   ! Tleaf - Tair (degrees C)

        bl = c * sqrt(Lm / max(u, 0.1))
        Tdiff = (bl / 1000) * (Jch/(2*Kair))

        Tleaf = Tair + Tdiff
    end function Tleaf

end module LeafTemp_Nobel


program Test_LeafTemp_Nobel

    use LeafTemp_Nobel, only: Tleaf

    real, parameter :: c = 4.0, Lm = 0.004
    
    real :: Tair, P, Rn, VPD, u, g_c
    real :: leafT

    integer :: ios

    do
        read (*, *, iostat=ios) Tair, P, Rn, VPD, u, g_c
        
        leafT = Tleaf(Tair, u, c, Lm, Rn)
        
        write (*, *) u, Rn, Tair, leafT, leafT - Tair

        if (ios /= 0) exit
    end do

end program Test_LeafTemp_Nobel
