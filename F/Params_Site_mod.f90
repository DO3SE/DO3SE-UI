module Params_Site_mod

    real, public, save  :: Rsoil = 200      ! Soil resistance in (s/m)

    real, public, save  :: soil_BD = 1.3    ! Soil bulk density (g/cm^3)
    real, public, save  :: soil_a = -5.5    ! SWC constant a - coarse = -4,
                                            ! medium = -5.5, fine = -7
    real, public, save  :: soil_b = -3.3    ! SWC constant b - coarse = -2.3, 
                                            ! medium = -3.3, fine = -5.4
    real, public, save  :: Fc_m = 0.193     ! Field capacity (m^3/m^3)

end module Params_Site_mod
