module Constants
    ! Angle conversions    
    real, public, parameter :: PI = 3.14159265358979312
    real, public, parameter :: DEG2RAD = 0.017453292519943295

    real, public, parameter :: k = 0.41         ! von Karman's constant
    real, public, parameter :: cp = 1005        ! specific head of air at constant 
                                                ! pressure for dry air (J/Kg/K)
    real, public, parameter :: g = 9.8          ! gravitational acceleration
    real, public, parameter :: v = 0.000015     ! kinematic viscosity of air (m^2/s at 20oC)
    real, public, parameter :: DO3 = 0.000015   ! molecular diffusivity of O3 in air (m^2/s)
    real, public, parameter :: DH2O = 0.000025  ! molecular diffusivity of H2O (m^2/s)
    real, public, parameter :: Dratio = 0.662   ! molecular diffusivity ratio (DO3/DH2O)
    real, public, parameter :: Pr = 0.72        ! Prandtl Number (Pr, -)

    real, public, parameter :: seaP = 101.325   ! Sea level air pressure in kPa

    real, public, parameter :: PARfrac = 0.45   ! approx. fraction of total radiation in 
                                                ! PAR waveband (0.45 to 0.5)
                                    
    real, public, parameter :: Ts_K = 273.16    ! Conversion from ToC to T Kelvin
    real, public, parameter :: Rmass = 287.0    ! mass gas constant for dry 
                                                ! air (J/Kg/K)
    
    real, public, parameter :: izR = 50         ! Intermediate "decoupled" height for 
                                                ! transfer of O3 and windspeed
    
    real, public, parameter :: SWC_sat = 0.4    ! Saturated soil water content, for
                                                ! soil water release curve

end module Constants
