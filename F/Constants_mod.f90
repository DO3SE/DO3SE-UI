module Constants_mod
    real, public, parameter :: uzR = 25

    real, public, parameter :: PI = 3.14159265358979312
    real, public, parameter :: DEG2RAD = PI / 180.0

    real, public, parameter :: PARfrac = 0.45   ! approx. fraction of total radiation in 
                                                ! PAR waveband (0.45 to 0.5)
                                    
    real, public, parameter :: Wm2_uE = 4.57                    ! converts W/m^2 to umol/m^2/s
    real, public, parameter :: Wm2_2uEPAR = PARfrac * Wm2_uE    ! converts W/m^2 to umol/m^2/s PAR
end module Constants_mod
