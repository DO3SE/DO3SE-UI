        module Params_Veg_mod

            real, public, save  :: LAI

            ! Growing season parameters
            real, public, save  :: T_min = 0    ! oC min temp for g
            real, public, save  :: T_opt = 21   ! oC opt temp for g
            real, public, save  :: T_max = 35   ! oC max temp for g

            real, public, save  :: VPD_min = 3.25   ! VPD for min g
            real, public, save  :: VPD_max = 1.0    ! VPD for max g
            
            real, public, save  :: SWP_min = -1.25  ! SWP for min g
            real, public, save  :: SWP_max = -0.05  ! SWP for max g

            real, public, save  :: albedo = 0.12    ! 0.2 for crops
                                                    ! 0.12 for needle leaf trees
                                                    ! 0.14 for moorland
                                                    ! 0.16 for broad leaf trees
                                                    
            real, public, save  :: root = 1.2       ! root depth (m)

        end module Params_Veg_mod
