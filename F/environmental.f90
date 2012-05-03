module Environmental

    public :: Calc_ftemp, Calc_fVPD, Calc_Flight

contains

    ! =======================================================================
    ! Calculate temperature effect on gsto, ftemp
    ! =======================================================================
    pure function do3se_ftemp(Ts_C, T_min, T_opt, T_max, fmin) result (ftemp)
        real, intent(in)    :: Ts_C     ! Air temperature (degrees C)
        real, intent(in)    :: T_min    ! Minimum temperature (degrees C)
        real, intent(in)    :: T_opt    ! Temperature for maximum g (degrees C)
        real, intent(in)    :: T_max    ! Maximum temperature (degrees C)
        real, intent(in)    :: fmin     ! Minimum ftemp
        real                :: ftemp    ! Output: temperature effect on gsto

        real :: bt

        bt = (T_max-T_opt)/(T_opt-T_min)
        ftemp = max(((Ts_C-T_min)/(T_opt-T_min))*((T_max-Ts_C)/(T_max-T_opt))**bt, fmin)
    end function do3se_ftemp

    !***************************************************************************
    ! Calculate ftemp
    !***************************************************************************
    subroutine Calc_ftemp()
        use Variables, only: ftemp
        use Inputs, only: Ts_c
        use Parameters, only: T_max, T_min, T_opt, fmin
        ftemp = do3se_ftemp(Ts_C, T_min, T_opt, T_max, fmin)
    end subroutine Calc_ftemp


    ! =======================================================================
    ! Calculate VPD effect on gsto, fVPD.
    !
    ! Note that VPD_min and VPD_max refer to the value for min. and max.
    ! gsto, therefore VPD_min should be greater than VPD_max.
    ! =======================================================================
    pure function do3se_fVPD(VPD, VPD_min, VPD_max, fmin) result (fVPD)
        real, intent(in)    :: VPD      ! Vapour pressure deficit (kPa)
        real, intent(in)    :: VPD_min  ! VPD for minimum gsto (kPa)
        real, intent(in)    :: VPD_max  ! VPD for maximum gsto (kPa)
        real, intent(in)    :: fmin     ! Minimum fVPD
        real                :: fVPD     ! Output: VPD effect on gsto

        fVPD = ((1 - fmin) * (VPD_min - VPD)/(VPD_min - VPD_max)) + fmin
        fVPD = max(fmin, min(1.0, fVPD))
    end function do3se_fVPD

    !***************************************************************************
    ! Calculate fVPD (vapour pressure deficit related g)
    !***************************************************************************
    subroutine Calc_fVPD()
        use Variables, only: fVPD
        use Inputs, only: VPD
        use Parameters, only: fmin, VPD_min, VPD_max

        fVPD = do3se_fVPD(VPD, VPD_min, VPD_max, fmin)
    end subroutine Calc_fVPD


    pure subroutine do3se_PAR_components(P, PARtotal, sinB, Idrctt, Idfuse)
        real, intent(in)    :: P            ! Atmospheric pressure (kPa)
        real, intent(in)    :: PARtotal     ! PAR irradiance (W m-2)
        real, intent(in)    :: sinB         ! sin(B), B = solar elevation angle
        real, intent(out)   :: Idrctt       ! Output: direct PAR irradiance (W m-2)
        real, intent(out)   :: Idfuse       ! Output: diffuse PAR irradiance (W m-2)

        real, parameter :: seaP = 101.325   ! Pressure at sea level (kPa)

        real :: m, pPARdir, pPARdif, pPARtotal, ST, fPARdir, fPARdif

        ! TODO: this was previously 1.0/sinB, which is correct?
        m = (P / seaP) / sinB

        pPARdir = 600 * exp(-0.185 * (P / seaP) * m) * sinB ! Potential direct PAR
        pPARdif = 0.4 * (600 - pPARdir) * sinB              ! Potential diffuse PAR
        pPARtotal = pPARdir + pPARdif                       ! Potential total PAR

        ST = max(0.21, min(0.9, PARtotal / pPARtotal))      ! Sky transmissivity

        ! Direct and diffuse fractions
        fPARdir = (pPARdir / pPARtotal ) * (1.0 - ((0.9 - ST) / 0.7)**(2.0/3.0))
        fPARdif = 1 - fPARdir

        ! Apply calculated direct and diffuse fractions to PARtotal
        Idrctt = fPARdir * PARtotal
        Idfuse = fPARdif * PARtotal
    end subroutine do3se_PAR_components


    !==========================================================================
    ! Calculate Flight and flight
    !==========================================================================
    subroutine Calc_Flight()
        ! TODO: document variables
        use Constants, only: seaP
        use Parameters, only: f_lightfac, cosA
        use Inputs, only: P, PAR, sinB
        use Variables, only: LAI, Flight, leaf_flight
        use Variables, only: LAIsun, LAIshade, PARsun, PARshade

        real :: PARdir, PARdif, Flightsun, Flightshade

        if (sinB > 0 .and. LAI > 0) then
            call do3se_PAR_components(P, PAR/4.57, sinB, PARdir, PARdif)
            PARdir = PARdir * 4.57
            PARdif = PARdif * 4.57

            LAIsun = (1 - exp(-0.5 * LAI / sinB)) * (2 * sinB)
            LAIshade = LAI - LAIsun

            PARshade = PARdif*exp(-0.5*(LAI**0.8))+0.07*PARdir*(1.1-(0.1*LAI))*exp(-sinB)
            PARsun = PARdir * 0.8 * (cosA/sinB) + PARshade

            ! TODO: does this need albedo?
            Flightsun = (1.0 - exp(-f_lightfac * PARsun))
            Flightshade = (1.0 - exp(-f_lightfac * PARshade))

            leaf_flight = (1.0 - exp(-f_lightfac * PAR))
            Flight = ((Flightsun * LAIsun) / LAI) + ((Flightshade * LAIshade) / LAI)
        else
            leaf_flight = 0
            Flight = 0
        end if
    end subroutine Calc_Flight

end module Environmental
