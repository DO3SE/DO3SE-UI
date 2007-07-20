        module Params_Veg_mod

            real, public, save :: LAI

            ! Growing season parameters
            real, public    :: T_min = 0    ! oC min temp for g
            real, public    :: T_opt = 21   ! oC opt temp for g
            real, public    :: T_max = 35   ! oC max temp for g
            real, public    :: VPD_min = 3.25   ! VPD for min g
            real, public    :: VPD_max = 1.0    ! VPD for max g
            real, public    :: SWP_min = -1.25  ! SWP for min g
            real, public    :: SWP_max = -0.05  ! SWP for max g


        end module Params_Veg_mod
