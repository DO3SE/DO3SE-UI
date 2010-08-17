module Environmental

    public :: Calc_ftemp, Calc_fVPD, Calc_Flight

contains

    !***************************************************************************
    ! Calculate ftemp
    !***************************************************************************
    subroutine Calc_ftemp()
        use Variables, only: ftemp

        use Inputs, only: Ts_c
        use Parameters, only: T_max, T_min, T_opt, fmin

        real :: bt 
        
        bt = (T_max - T_opt) / (T_opt - T_min)
        ftemp = max(((Ts_c-T_min)/(T_opt-T_min))*((T_max-Ts_c)/(T_max-T_opt))**bt, fmin)
    end subroutine Calc_ftemp

    !***************************************************************************
    ! Calculate fVPD (vapour pressure deficit related g)
    !***************************************************************************
    subroutine Calc_fVPD()
        use Variables, only: fVPD

        use Inputs, only: VPD
        use Parameters, only: fmin, VPD_min, VPD_max

        fVPD = ((1 - fmin)*(VPD_min - VPD)/(VPD_min - VPD_max)) + fmin
        fVPD = max(fVPD, fmin)

        if ( fVPD > 1 ) then
            fVPD = 1
        end if
    end subroutine Calc_fVPD
    
    !==========================================================================
    ! Calculate Flight and flight
    !==========================================================================
    subroutine Calc_Flight()
        ! TODO: document variables
        use Constants, only: seaP
        use Parameters, only: f_lightfac, cosA
        use Inputs, only: P, PAR, sinB
        use Variables, only: LAI, Flight, leaf_flight
        use Variables, only: pPARdir, pPARdif, fPARdir, fPARdif, &
                LAIsun, LAIshade, PARsun, PARshade

        real :: m, pPARtotal, ST, PARdir, PARdif, Flightsun, &
                Flightshade

        if (sinB > 0 .and. LAI > 0) then
            m = 1.0 / sinB

            ! Potential direct and diffuse PAR
            pPARdir = 600 * exp(-0.185 * (P/seaP) * m) * sinB
            pPARdif = 0.4 * (600 - pPARdir) * sinB
            pPARtotal = pPARdir + pPARdif

            ! Sky transmissivity (with PAR converted to W/m^2)
            ST = min(0.9, max(0.21, (PAR/4.57)/pPARtotal))

            fPARdir = (pPARdir/pPARtotal) * (1-((0.9-ST)/0.7)**(2.0/3.0))
            fPARdif = 1 - fPARdir

            PARdir = fPARdir * PAR
            PARdif = fPARdif * PAR

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
