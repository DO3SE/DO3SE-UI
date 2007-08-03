module Params_Veg_mod

    real, public, save  :: T_min = 0    ! oC min temp for g
    real, public, save  :: T_opt = 21   ! oC opt temp for g
    real, public, save  :: T_max = 35   ! oC max temp for g

    real, public, save  :: VPD_min = 3.25   ! VPD for min g
    real, public, save  :: VPD_max = 1.0    ! VPD for max g
    
    real, public, save  :: SWP_min = -1.25  ! SWP for min g
    real, public, save  :: SWP_max = -0.05  ! SWP for max g

    ! Boundary gs values
    real, public, save  :: gmax = 148       ! mmol O3 m^-2 PLA s^-1
    real, public, save  :: fmin = 0.13      ! minimum gs

    real, public, save  :: albedo = 0.12    ! 0.2 for crops
                                            ! 0.12 for needle leaf trees
                                            ! 0.14 for moorland
                                            ! 0.16 for broad leaf trees
    
    real, public, save  :: root = 1.2       ! root depth (m)

    real, public, save  :: SGS = 121        ! Start of bulk canopy growth period
    real, public, save  :: EGS = 273        ! End of bulk canopy growth period
    real, public, save  :: Astart = 121     ! Start of upper leaf growth period
    real, public, save  :: Aend = 273       ! End of upper leaf growth period
    real, public, save  :: LAI_min = 0      ! Min LAI in m^2/m^2
    real, public, save  :: LAI_max = 4.0    ! Max LAI in m^2/m^2
    real, public, save  :: Ls = 30          ! time from LAI_min to LAI_max
    real, public, save  :: Le = 30          ! time from LAI_max to LAI_min

    real, public, save  :: cosA = 0.5       ! A = mean leaf inclination (60 degs)
    real, public, save  :: f_lightfac = 0.006 ! single leaf flight coefficient
                                            
    ! fphen polygon parameters
    real, public, save  :: fphen_a = 0      ! fphen at SGS
    real, public, save  :: fphen_b = 0      ! fphen at Astart
    real, public, save  :: fphen_c = 1.0    ! fphen midway during season
    real, public, save  :: fphen_d = 0      ! fphen at Aend and EGS
    real, public, save  :: fphenS = 15      ! period to fphen_c
    real, public, save  :: fphenE = 20      ! period to fphen_d

    real, public, save  :: Rext = 2500      ! external plant cuticle resistance in s/m
    real, public, save  :: Rinc_b = 14      ! Rinc co-efficient

    real, public, save  :: Lm = 0.05        ! Leaf dimension (m)
    real, public, save  :: Y = 1.6          ! Threshold (Y) in AFstY, nmol O3 m-2 s-1
    

end module Params_Veg_mod
