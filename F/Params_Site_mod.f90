        module Params_Site_mod

            real, public, save  :: Rsoil            ! Soil resistance in (m/s) ?

            real, public, save  :: soil_BD = 1.6    ! Soil bulk density (g/cm^3)
            real, public, save  :: soil_a = -4      ! SWC constant a - coarse = -4,
                                                    ! medium = -5.5, fine = -7
            real, public, save  :: soil_b = -2.3    ! SWC constant b - coarse = -2.3, 
                                                    ! medium = -3.3, fine = -5.4
            real, public, save  :: Fc_m = 0.15      ! Field capacity (m^3/m^3)

        end module Params_Site_mod
