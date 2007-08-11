!*******************************************************************************
! Variables.f90 - Global variables module
!
! Contains all variables used in more than one part of the model
!*******************************************************************************

module Variables
    
    ! Day of year for previous dataset
    real*8, public, save :: dd_prev = -1

    ! Environmental
    real*8, public, save  :: ftemp
    real*8, public, save  :: fVPD

    ! Evapotranspiration
    real*8, public, save  :: PEt  ! Potential evapotranspiration
    real*8, public, save  :: AEt  ! Actual evapotranspiration
    real*8, public, save  :: Ei   ! Evaporation of intercepted precip

    ! Irradiance
    real*8, public, save  :: Flight       ! Canopy average gsto in relation to canopy light
    real*8, public, save  :: leaf_flight  ! light related g
    real*8, public, save  :: LAIsunfrac
    real*8, public, save  :: PARshade
    real*8, public, save  :: PARsun

    ! Phenology
    real*8, public, save  :: LAI
    real*8, public, save  :: SAI
    real*8, public, save  :: fphen
    real*8, public, save  :: leaf_fphen

    ! R
    real*8, public, save  :: Ra
    real*8, public, save  :: Ra_O3
    real*8, public, save  :: Rb
    real*8, public, save  :: Rsur
    real*8, public, save  :: Rinc
    real*8, public, save  :: Rsto
    real*8, public, save  :: Rgs

    real*8, public, save  :: ustar
    real*8, public, save  :: Gsto, Gsto_PEt

    ! Soil
    real*8, public, save :: PWP        ! Calculated PWP in m3/3
    real*8, public, save :: ASW        ! Calculated ASW in m3/m3
    real*8, public, save :: Sn_star    ! Calculated Sn* in m3/m3
    real*8, public, save :: Sn         ! soil Water storage capacity
    real*8, public, save :: per_vol    ! % volumetric water content
    real*8, public, save :: SMD        ! soil moisture deficit in mm
    real*8, public, save :: SWP        ! Soil water potential in MPa
    real*8, public, save :: WC         ! water content
    real*8, public, save :: precip     ! Previous day's total precipitation
    real*8, public, save :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations
    real*8, public, save :: fSWP

    ! O3_Flux
    real*8, public, save :: O3_ppb, O3_nmol_m3, Vd
    real*8, public, save :: Ftot

    ! O3_Effects
    real*8, public, save :: Fst, AFstY, AOT40

end module Variables

