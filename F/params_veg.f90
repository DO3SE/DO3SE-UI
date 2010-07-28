module Params_Veg

    real, public, save :: T_min = 0    ! oC min temp for g
    real, public, save :: T_opt = 21   ! oC opt temp for g
    real, public, save :: T_max = 35   ! oC max temp for g

    real, public, save :: VPD_min = 3.25    ! VPD for min g
    real, public, save :: VPD_max = 1.0     ! VPD for max g
    real, public, save :: VPD_crit = 1000   ! Critical daily VPD sum (kPa)
    
    real, public, save :: SWP_min = -1.25   ! SWP for min g
    real, public, save :: SWP_max = -0.05   ! SWP for max g

    ! Boundary gs values
    real, public, save :: gmax = 148        ! mmol O3 m^-2 PLA s^-1
    real, public, save :: gmorph = 1.0      ! sun/shade leaf morphology modifier
    real, public, save :: fmin = 0.13       ! minimum gs

    real, public, save :: albedo = 0.12     ! 0.2 for crops
                                            ! 0.12 for needle leaf trees
                                            ! 0.14 for moorland
                                            ! 0.16 for broad leaf trees
    
    real, public, save :: root = 1.2        ! root depth (m)
    real, public, save :: h = 25            ! Canopy height (m)
    real, public, save :: zo                ! Roughness length (m)
    real, public, save :: d                 ! Displacement height (m)

    ! Growing season
    real, public, save :: SGS = 121         ! Start of bulk canopy growth period
    real, public, save :: EGS = 273         ! End of bulk canopy growth period

    ! Leaf area index
    real, public, save :: LAI_a = 0.0       ! First LAI point (at SGS)
    real, public, save :: LAI_b = 4.0       ! Second LAI point
    real, public, save :: LAI_c = 4.0       ! Third LAI point
    real, public, save :: LAI_d = 0.0       ! Last LAI point (at EGS)
    real, public, save :: LAI_1 = 30        ! Period from LAI_a to LAI_b
    real, public, save :: LAI_2 = 30        ! Period from LAI_c to LAI_d

    ! fphen polygon (see Calc_fphen in phenology.f90)
    real, public, save :: fphen_limA = 0    ! Start of soil water limitation
    real, public, save :: fphen_limB = 0    ! End of soil water limitation
    real, public, save :: fphen_a = 0.0     ! First fphen point (at SGS)
    real, public, save :: fphen_b = 1.0
    real, public, save :: fphen_c = 1.0     ! fphen during soil water limitation
    real, public, save :: fphen_d = 1.0
    real, public, save :: fphen_e = 0.0     ! Last fphen point (at EGS)
    real, public, save :: fphen_1 = 15      ! Period from fphen_a to fphen_b
    real, public, save :: fphen_2 = 0       ! Period from fphen_b to fphen_c
    real, public, save :: fphen_3 = 0       ! Period from fphen_c to fphen_d
    real, public, save :: fphen_4 = 20      ! Period from fphen_d to fphen_e


    ! leaf fphen polygon
    real, public, save :: Astart = 121      ! Start of upper leaf growth period
    real, public, save :: Aend = 273        ! End of upper leaf growth period
    real, public, save :: leaf_fphen_a = 0.0 ! First fphen point (at Astart)
    real, public, save :: leaf_fphen_b = 1.0 ! Second fphen point (plateau)
    real, public, save :: leaf_fphen_c = 0.0 ! Last fphen point (at Aend)
    real, public, save :: leaf_fphen_1 = 15 ! Time from leaf_fphen_a to leaf_fphen_b
    real, public, save :: leaf_fphen_2 = 30 ! Time from leaf_fphen_b to leaf_fphen_c

    real, public, save :: cosA = 0.5        ! A = mean leaf inclination (60 degs)
    real, public, save :: f_lightfac = 0.006 ! single leaf flight coefficient
                                            
    real, public, save :: Rext = 2500       ! external plant cuticle resistance in s/m
    real, public, save :: Rinc_b = 14       ! Rinc co-efficient

    real, public, save :: Lm = 0.05         ! Leaf dimension (m)
    real, public, save :: Y = 1.6           ! Threshold (Y) in AFstY, nmol O3 m-2 s-1
    
    public :: Derive_d_zo

contains

    !==========================================================================
    ! Derive the displacement height and roughness length from the height of 
    ! the canopy.
    !==========================================================================
    subroutine Derive_d_zo()
        d = h * 0.7
        zo = h * 0.1
    end subroutine Derive_d_zo

end module Params_Veg
