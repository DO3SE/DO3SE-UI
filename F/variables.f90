!*******************************************************************************
! Variables.f90 - Global variables module
!
! Contains all variables used in more than one part of the model
!*******************************************************************************

module Variables
    
    ! Day of year for previous dataset
    real, public, save :: dd_prev = -1

    ! Environmental
    real, public, save  :: ftemp
    real, public, save  :: fVPD

    ! Evapotranspiration
    real, public, save  :: PEt  ! Potential evapotranspiration
    real, public, save  :: AEt  ! Actual evapotranspiration
    real, public, save  :: Ei   ! Evaporation of intercepted precip
    real, public, save  :: Es   ! Evaporation of soil water

    ! Irradiance
    real, public, save  :: Flight       ! Canopy average gsto in relation to canopy light
    real, public, save  :: leaf_flight  ! light related g
    real, public, save  :: Rn       ! Net radiation (MJ/m2/h)
    real, public, save  :: Rn_W     ! Net radiation (W/m2)

    ! Phenology
    real, public, save  :: LAI
    real, public, save  :: SAI
    real, public, save  :: fphen
    real, public, save  :: leaf_fphen

    ! R
    real, public, save  :: Ra
    real, public, save  :: Rb
    real, public, save  :: Rsur
    real, public, save  :: Rinc
    real, public, save  :: Rsto
    real, public, save  :: Rgs
    ! Intermediate R variables
    real, public, save  :: Ra_i

    real, public, save  :: Gsto, Gsto_PEt

    ! Soil
    real, public, save :: SWP_min_vol ! SWP_min in m3/m3
    real, public, save :: Sn_star    ! Calculated Sn* in m3/m3
    real, public, save :: ASW        ! Calculated ASW in m
    real, public, save :: Sn         ! Soil water in m3/m3
    real, public, save :: per_vol    ! % volumetric water content
    real, public, save :: SMD        ! soil moisture deficit in m
    real, public, save :: SWP        ! Soil water potential in MPa
    real, public, save :: precip     ! Previous day's total precipitation
    real, public, save :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations
    real, public, save :: fSWP

    ! O3
    real, public, save :: O3_ppb, O3_nmol_m3, Vd
    real, public, save :: Ftot
    real, public, save :: Fst, AFstY, OT40, AOT40

    ! More variables, for testing
    real, public, save :: sinB
    real, public, save :: pPARdir
    real, public, save :: pPARdif
    real, public, save :: fPARdir
    real, public, save :: fPARdif
    real, public, save :: LAIsun
    real, public, save :: LAIshade
    real, public, save :: PARsun
    real, public, save :: PARshade
    real, public, save :: eact

end module Variables

