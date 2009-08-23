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

    ! Irradiance
    real, public, save  :: Flight       ! Canopy average gsto in relation to canopy light
    real, public, save  :: leaf_flight  ! light related g
    real, public, save  :: Rn       ! net radiation

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
    real, public, save :: PWP        ! Calculated PWP in m3/3
    real, public, save :: ASW        ! Calculated ASW in m3/m3
    real, public, save :: Sn_star    ! Calculated Sn* in m3/m3
    real, public, save :: Sn         ! soil Water storage capacity
    real, public, save :: per_vol    ! % volumetric water content
    real, public, save :: SMD        ! soil moisture deficit in mm
    real, public, save :: SWP        ! Soil water potential in MPa
    real, public, save :: WC         ! water content
    real, public, save :: precip     ! Previous day's total precipitation
    real, public, save :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations
    real, public, save :: fSWP

    ! O3
    real, public, save :: O3_ppb, O3_nmol_m3, Vd
    real, public, save :: Ftot
    real, public, save :: Fst, AFstY, OT40, AOT40

end module Variables

