module Irradiance

    !real, private, save :: sinB   ! Solar elevation angle
    real, private, save :: h      ! Hour angle of the sun (radians)
    real, private, save :: dec    ! Declination (radians)

    public :: Calc_sinB
    public :: Calc_Flight
    public :: Copy_Rn
    public :: Calc_Rn

contains
    
    !==========================================================================
    ! Calculate the solar elevation angle, using the geographical location of 
    ! the site and the time of day and day of year.
    !==========================================================================
    subroutine Calc_sinB()
        ! TODO: document variables
        use Params_Site, only: lat, lon
        use Inputs, only: dd, hr
        use Functions, only: deg2rad, rad2deg
        use Variables, only: sinB

        real :: f, e, t0, LC, lonm

        ! Calculate the longitudinal meridian
        lonm = nint(lon / 15.0) * 15.0

        ! Solar noon correction for day of year
        f = deg2rad(279.575 + (0.9856 * dd))
        e = (-104.7*sin(f) + 596.2*sin(2*f) + 4.3*sin(3*f) - 12.7*sin(4*f) &
            - 429.3*cos(f) - 2.0*cos(2*f) + 19.3*cos(3*f)) / 3600

        ! Solar noon, with day of year and longitudinal correction
        LC = (lon - lonm) / 15
        t0 = 12 - LC - e

        ! Hour-angle of the sun
        h = deg2rad(15 * (hr - t0))

        ! Declination (radians)
        dec = deg2rad(-23.4 * cos(deg2rad(360 * ((dd + 10) / 365))))

        sinB = sin(deg2rad(lat))*sin(dec) + cos(deg2rad(lat))*cos(dec)*cos(h)
        sinB = max(0.0, sinB)
    end subroutine Calc_sinB

    
    !==========================================================================
    ! Calculate Flight and flight
    !==========================================================================
    subroutine Calc_Flight()
        ! TODO: document variables
        use Constants, only: seaP
        use Params_Veg, only: f_lightfac, cosA
        use Inputs, only: P, PAR
        use Variables, only: LAI, Flight, leaf_flight
        use Variables, only: sinB
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

            ST = min(0.9, max(0.21, PAR/pPARtotal))

            fPARdir = (pPARdif/pPARtotal) * (1-((0.9-ST)/0.7)**(2.0/3.0))
            fPARdif = 1 - fPARdir

            PARdir = fPARdir * PAR
            PARdif = fPARdif * PAR

            LAIsun = (1 - exp(-0.5 * (LAI/sinB)) * (2*sinB))
            LAIshade = LAI - LAIsun

            PARshade = PARdif*exp(-0.5*(LAI**0.8))+0.07*PARdir*(1.1-(0.1*LAI))*exp(-sinB)
            PARsun = PARdir * 0.8 * (cosA/sinB) + PARshade

            ! TODO: does this need albedo?
            Flightsun = (1.0 - exp(-f_lightfac * PARsun))
            Flightshade = (1.0 - exp(-f_lightfac * PARshade))

            leaf_flight = Flightsun
            Flight = ((Flightsun * LAIsun) / LAI) + ((Flightshade * LAIshade) / LAI)
        else
            leaf_flight = 0
            Flight = 0
        end if
    end subroutine Calc_Flight

    !==========================================================================
    ! Use net radiation input rather than deriving it
    !==========================================================================
    subroutine Copy_Rn()
        use Inputs, only: Rn_input => Rn
        use Variables, only: Rn, Rn_W
        Rn = Rn_input
        Rn_W = Rn * 277.8
    end subroutine Copy_Rn

    !==========================================================================
    ! Calculate net radiation
    !==========================================================================
    subroutine Calc_Rn()
        ! TODO: document variables
        use Params_Site, only: elev, lat
        use Params_Veg, only: albedo
        use Inputs, only: R, Ts_C, VPD, dd
        use Variables, only: Rn, Rn_W
        use Constants, only: pi
        use Functions, only: deg2rad, rad2deg
        use Variables, only: sinB, eact

        real :: R_MJ, Ts_K, dr, Re, pR, esat, Rnl, Rns, lat_rad, h1, h2

        ! Constants
        real, parameter :: Gsc = 0.082            ! Solar constant (MJ/m^2/min)
        real, parameter :: SBC = 4.903e-9 / 24    ! Stephan Boltzman constant

        lat_rad = deg2rad(lat)

        esat = 0.611 * exp((17.27 * Ts_C) / (Ts_C + 237.3))
        eact = esat - VPD

        if (sinB > 0) then
            ! Unit conversions
            R_MJ = R * 0.0036
            Ts_K = Ts_C + 273.16

            ! Hour angle stuff
            h1 = h - (pi/24)
            h2 = h + (pi/24)

            dr = 1 + (0.033 * cos(((2 * pi) / 365) * dd))
            ! External radiation (with fix to stop div by zero)
            ! TODO: fix this to be less hackish
            Re = max(0.00000000001, &
                    ((12 * 60) / pi) * Gsc * dr &
                        * ((h2 - h1) * sin(lat_rad) * sin(dec) &
                            + cos(lat_rad) * cos(dec) * (sin(h2) - sin(h1))))
            !Re = max(0.0, ((12*60)/pi)*Gsc*dr*sinB)

            ! Calculate net longwave radiation
            pR = (0.75 + (2e-5 * elev)) * Re

            Rnl = max(0.0, (SBC*(Ts_K**4)) * (0.34-(0.14*sqrt(eact))) * ((1.35*(min(1.0, R_MJ/pR)))-0.35))
            Rns = (1 - albedo) * R_MJ

            Rn = Rns - Rnl
        else
            Rn = 0
        end if

        ! Calculate Rn in W/m2
        Rn_W = Rn * 277.8
    end subroutine Calc_Rn

end module Irradiance
