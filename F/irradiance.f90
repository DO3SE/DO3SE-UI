module Irradiance

    real, private, save :: sinB   ! Solar elevation angle

    public :: Calc_sinB
    public :: Calc_Flight
    public :: Calc_Rn_Copy
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

        real :: f, e, t0, h, dec, LC, lonm

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
        h = 15 * (hr - t0)

        ! Declination (radians)
        dec = -23.4 * cos(deg2rad(360 * ((dd + 10) / 365)))

        ! TODO: check this value!!!
        sinB = sin(deg2rad(lat))*sin(dec) + cos(deg2rad(lat))*cos(dec)*cos(deg2rad(h))
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

        m = (P/seaP) / sinB

        ! Potential direct and diffuse PAR
        pPARdir = 600 * exp(-0.185 * (P/seaP) * m) * sinB
        pPARdif = 0.4 * (600 - pPARdir) * sinB
        pPARtotal = pPARdir + pPARdif

        ST = min(0.9, max(0.21, PAR/pPARtotal))

        fPARdir = (pPARdif/pPARtotal) * (1-((0.9-ST)/0.7)**(2/3))
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
        ! TODO: leaf_flight ???
    end subroutine Calc_Flight

    !==========================================================================
    ! Use net radiation input rather than deriving it
    !==========================================================================
    subroutine Calc_Rn_Copy()
        use Inputs, only: Rn_input => Rn
        use Variables, only: Rn
        Rn = Rn_input
    end subroutine Calc_Rn_Copy

    !==========================================================================
    ! Calculate net radiation
    !==========================================================================
    subroutine Calc_Rn()
        ! TODO: document variables
        use Params_Site, only: lat, lon, elev
        use Params_Veg, only: albedo
        use Inputs, only: R, Ts_C, VPD
        use Variables, only: Rn

        real :: R_MJ, Ts_K, dr, Re, pR, esat, eact, Rnl, Rns

        ! Constants
        real, parameter :: Gsc = 0.082            ! Solar constant (MJ/m^2/min)
        real, parameter :: SBC = 4.903e-9 / 24    ! Stephan Boltzman constant

        ! Unit conversions
        R_MJ = R * 0.0036
        Ts_K = Ts_C + 273.15

        dr = 1 + (0.033 * cos(((2 * pi) / 365) * td))
        Re = max(0.0, ((12 * 60) / pi) * Gsc * dr * sinB)

        ! Calculate net longwave radiation
        pR = (0.75 + (2e-5 * elev)) * Re
        esat = 0.611 * exp((17.27 * Ts_C)/(Ts_K))
        eact = esat - VPD

        Rnl = (SBC*(Ts_c**4)) * (0.34-(0.14*sqrt(eact))) * ((1.35*(min(1.0, R_MJ/pR)))-0.35)
        Rns = (1 - albedo) * R_MJ

        Rn = Rns - Rnl
    end subroutine Calc_Rn

end module Irradiance
