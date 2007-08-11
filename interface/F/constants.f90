module Constants
    ! Angle conversions    
    real*8, public, parameter :: PI = 3.14159265358979312
    real*8, public, parameter :: DEG2RAD = 0.017453292519943295

    real*8, public, parameter :: k = 0.41         ! von Karman's constant
    real*8, public, parameter :: cp = 1005        ! specific head of air at constant 
                                                ! pressure for dry air (J/Kg/K)
    real*8, public, parameter :: g = 9.8          ! gravitational acceleration
    real*8, public, parameter :: v = 0.000015     ! kinetic viscosity of air (m^2/s at 20oC)
    real*8, public, parameter :: DO3 = 0.000015   ! molecular diffusivity of OR in 
                                                ! air relative to water vapour (m^2/s)
    real*8, public, parameter :: Pr = 0.72        ! Prandtl Number (Pr, -)
    real*8, public, parameter :: uzR = 25         ! Reference height for wind speed
    real*8, public, parameter :: czR = 25         ! Reference height for O3 concentration
    real*8, public, parameter :: h = 25           ! Canopy height
    real*8, public, parameter :: zo = h * 0.1     ! Roughness length
    real*8, public, parameter :: d = h * 0.7      ! Displacement height

    real*8, public, parameter :: seaP = 101.325   ! Sea level air pressure in kPa

    real*8, public, parameter :: PARfrac = 0.45   ! approx. fraction of total radiation in 
                                                ! PAR waveband (0.45 to 0.5)
                                    
    real*8, public, parameter :: Wm2_uE = 4.57                    ! converts W/m^2 to umol/m^2/s
    real*8, public, parameter :: Wm2_2uEPAR = PARfrac * Wm2_uE    ! converts W/m^2 to umol/m^2/s PAR

    real*8, public, parameter :: Ts_K = 273.15    ! Conversion from ToC to T Kelvin

end module Constants
