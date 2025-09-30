module Environmental

    public :: Calc_ftemp, Calc_fVPD, Calc_Flight, Calc_PAR_from_cloudfrac

contains

    !***************************************************************************
    ! Calculate ftemp
    !
    ! Made daylight only to match EMEP
    !***************************************************************************
    subroutine Calc_ftemp()
        use Variables, only: ftemp

        use Inputs, only: Ts_c, PAR
        use Parameters, only: T_max, T_min, T_opt, fmin

        real :: bt
        if (PAR > 0) then
            bt = (T_max - T_opt) / (T_opt - T_min)
            ftemp = max(((Ts_c-T_min)/(T_opt-T_min))*((T_max-Ts_c)/(T_max-T_opt))**bt, fmin)
        else
            ftemp = 0
        endif

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
    ! Calculate Flight and flight with PAR
    !==========================================================================
    subroutine Calc_Flight()
        use Constants, only: seaP, Wm2_uE
        use Parameters, only: f_lightfac, cosA
        use Inputs, only: sinB, PAR
        use Variables, only: LAI, Flight, leaf_flight, Flightsun, Flightshade
        use Variables, only: fPARdir, fPARdif, &
                LAIsun, LAIshade, PARsun, PARshade, PARdir, PARdif

        real :: cosT

        cosT = sinB
        if (sinB > 0 .and. LAI > 0) then
             PARdir = fPARdir * PAR
             PARdif = fPARdif * PAR

            ! In canopy PAR
            LAIsun = (1 - exp(-0.5 * LAI / cosT)) * (cosT/cosA)
            LAIshade = LAI - LAIsun

            PARshade = PARdif*exp(-0.5*(LAI**0.7))+0.07*PARdir*(1.1-(0.1*LAI))*exp(-cosT)
            PARsun = PARdir * cosA/cosT + PARshade

            leaf_flight = (1.0 - exp(-f_lightfac * PAR * Wm2_uE))

            ! Setup for g_sun and fst_sunlit as in EMEP model.

            ! Canopy
            ! TODO: does this need albedo?
            Flightsun = (1.0 - exp(-f_lightfac * PARsun * Wm2_uE))
            Flightshade = (1.0 - exp(-f_lightfac * PARshade * Wm2_uE))
            Flight = ((Flightsun * LAIsun) / LAI) + ((Flightshade * LAIshade) / LAI)
        else
            PARdir = 0
            PARdif = 0

            PARshade = 0
            PARsun = 0

            leaf_flight = 0
            Flight = 0
            Flightsun = 0
            Flightshade = 0
        end if
    end subroutine Calc_Flight


    !==========================================================================
    ! Calculate PAR from cloudfrac
    !
    ! Calculates ST and PARdir and PARdif

    ! From discussion on EMEP email chain 03-2021
    !==========================================================================
    subroutine Calc_PAR_from_cloudfrac()
        use Constants, only: seaP, Wm2_uE
        use Inputs, only: P, sinB, cloudfrac, PAR
        use Variables, only: pPARdir, pPARdif, fPARdir, fPARdif, &
              PARdir, PARdif, ST, LAI

        real :: m, pPARtotal, cosT

        cosT = sinB
        if (sinB > 0 .and. LAI > 0) then
            ! Note: Assuming sinB = cos0

            m = 1.0 / cosT
            ! Above canopy PAR
            ! Potential direct and diffuse PAR for clear sky
            pPARdir = 600 * exp(-0.185 * (P/seaP) * m) * cosT
            pPARdif = 0.4 * (600 - pPARdir) * cosT
            pPARtotal = pPARdir + pPARdif

            ! Sky transmissivity from cloud frac
            ST = 1.0 - (0.75 * (cloudFrac ** 3.4))

            ! PARTITIONING SOLAR RADIATION INTO DIRECT AND DIFFUSE,
            ! VISIBLE AND NEAR-INFRARED COMPONENTS*
            ! A. WEISS and J.M. NORMAN
            ! Eq 11
            ! A = 0.9 EMEP Vars
            ! B = 0.7 EMEP Vars
            if (ST < 0.9) then
                fPARdir = (pPARdir/pPARtotal) * (1-((0.9-ST)/0.7)**(2.0/3.0))
            else
                fPARdir = (pPARdir/pPARtotal)
            end if

            fPARdif = 1 - fPARdir

            PAR = ST * pPARtotal ! W/m2
            PARdir = fPARdir * PAR
            PARdif = PAR - PARdir
        else
            ST = 0
            PAR = 0
            PARdir = 0
            PARdif = 0
            pPARdir = 0
            fPARdir = 1
            pPARdif = 0
            fPARdif = 0
        end if
    end subroutine Calc_PAR_from_cloudfrac


    !==========================================================================
    ! Calculate Sky transmissivity from PAR
    !==========================================================================
    subroutine Calc_ST_from_PAR()
        use Constants, only: seaP
        use Inputs, only: P, sinB, PAR
        use Variables, only: pPARdir, pPARdif, fPARdir, fPARdif, &
              ST, LAI

        real :: m, pPARtotal

        if (sinB > 0 .and. LAI > 0) then
            m = 1.0 / sinB
            ! Above canopy PAR
            ! Potential direct and diffuse PAR
            pPARdir = 600 * exp(-0.185 * (P/seaP) * m) * sinB
            pPARdif = 0.4 * (600 - pPARdir) * sinB
            pPARtotal = pPARdir + pPARdif

            ! Sky transmissivity from cloud frac
            ST = min(0.9, max(0.21, PAR/pPARtotal))

            ! A = 0.9
            ! B = 0.7
            fPARdir = 0 !(pPARdir/pPARtotal) * (1-((0.9-ST)/0.7)**(2.0/3.0))
            fPARdif = 1 - fPARdir
        else
            ST = 0
            fPARdir=0
            fPARdir=0
        end if
    end subroutine Calc_ST_from_PAR

    !==========================================================================
    ! Calculate Flight and flight with cloudFrac
    !==========================================================================
    ! subroutine Calc_Flight_cloudfrac()
    !     use Constants, only: seaP
    !     use Parameters, only: f_lightfac, cosA
    !     use Inputs, only: P, sinB, cloudFrac
    !     use Variables, only: LAI, Flight, leaf_flight
    !     use Variables, only: pPARdir, pPARdif, fPARdir, fPARdif, &
    !             LAIsun, LAIshade, PARsun, PARshade, PARdir, PARdif, ST

    !     real :: m, pPARtotal, Flightsun, &
    !             Flightshade

    !     if (sinB > 0 .and. LAI > 0) then
    !         ! TODO: We are duplicating code here to calc par again
    !         ! Note: Assuming sinB = cos0

    !         m = 1.0 / sinB
    !         ! Above canopy PAR
    !         ! Potential direct and diffuse PAR for clear sky
    !         pPARdir = 600 * exp(-0.185 * (P/seaP) * m) * sinB
    !         pPARdif = 0.4 * (600 - pPARdir) * sinB
    !         pPARtotal = pPARdir + pPARdif

    !         ! Sky transmissivity from cloud frac
    !         ST = 1.0 - 0.75 * (cloudFrac) ** 3.4

    !         ! A = 0.9
    !         ! B = 0.7
    !         if (cloudFrac < 0.9) then
    !             fPARdir = (pPARdir/pPARtotal) * (1-((0.9-ST)/0.7)**(2.0/3.0))
    !         else
    !             fPARdir = (pPARdir/pPARtotal)
    !         end if

    !         fPARdif = 1 - fPARdir

    !         PARh = ST * pPARtotal
    !         PARdir = fPARdir * PARh
    !         PARdif = PARh - PARdir

    !         ! In canopy PAR
    !         LAIsun = (1 - exp(-0.5 * LAI / sinB)) * (sinB/cosA)
    !         LAIshade = LAI - LAIsun

    !         PARshade = PARdif*exp(-0.5*(LAI**0.7))+0.07*PARdir*(1.1-(0.1*LAI))*exp(-sinB)
    !         PARsun = PARdir * (cosA/sinB) + PARshade

    !         ! TODO: does this need albedo?
    !         Flightsun = (1.0 - exp(-f_lightfac * PARsun))
    !         Flightshade = (1.0 - exp(-f_lightfac * PARshade))

    !         leaf_flight = (1.0 - exp(-f_lightfac * PARh))
    !         Flight = ((Flightsun * LAIsun) / LAI) + ((Flightshade * LAIshade) / LAI)
    !     else
    !         PARdir = 0
    !         PARdif = 0

    !         PARshade = 0
    !         PARsun = 0

    !         leaf_flight = 0
    !         Flight = 0
    !     end if
    ! end subroutine Calc_Flight_cloudfrac

end module Environmental

