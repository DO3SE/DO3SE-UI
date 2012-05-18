!*******************************************************************************
! Variables.f90 - Global variables module
!
! Contains all variables used in more than one part of the model
!*******************************************************************************

module Variables
    
    ! Day of year for previous row
    real, public, save :: dd_prev = -1

    ! Environmental
    real, public, save  :: ftemp
    real, public, save  :: fVPD
    real, public, save  :: Flight       ! Canopy average gsto in relation to canopy light
    real, public, save  :: leaf_flight  ! light related g

    ! Phenology
    real, public, save  :: LAI
    real, public, save  :: SAI
    real, public, save  :: fphen
    real, public, save  :: leaf_fphen

    ! Soil water / evapotranspiration
    real, public, save  :: Ei   ! Evaporation of intercepted precipitation
    real, public, save  :: PEt  ! Potential plant transpiration
    real, public, save  :: Et   ! Actual plant transpiration
    real, public, save  :: Es   ! Evaporation of soil water
    real, public, save  :: AEt  ! Actual evapotranspiration (combining plant
                                ! transpiration and soil evaporation)
    real, public, save :: Sn_star    ! Calculated Sn* in m3/m3
    real, public, save :: ASW        ! Calculated ASW in m
    real, public, save :: Sn         ! Soil water in m3/m3
    real, public, save :: per_vol    ! % volumetric water content
    real, public, save :: SMD        ! soil moisture deficit in m
    real, public, save :: SWP        ! Soil water potential in MPa
    real, public, save :: fSWP
    real, public, save :: Sn_diff
    real, public, save :: fXWP
    real, public, save :: LWP           ! Leaf water potential (MPa)
    real, public, save :: delta_LWP     ! Change in LWP between hours
    real, public, save :: fLWP
    real, public, save :: Sn_meas       ! Soil water above measurement depth
    real, public, save :: Sn_diff_meas  ! Change in Sn_meas
    real, public, save :: SWP_meas      ! SWP for soil above measurement depth
    real, public, save :: SMD_meas      ! SMD for soil above measurement depth
    real, public, save :: fPAW
    logical, public, save :: Es_blocked ! Is soil evaporation blocked?

    ! R
    real, public, save  :: Ra
    real, public, save  :: Rb       ! Boundary resistance to O3
    real, public, save  :: Rb_H2O   ! Boundary resistance to H2O
    real, public, save  :: Rsur
    real, public, save  :: Rinc
    real, public, save  :: Rgs
    ! Resistances used in "transfer functions"
    real, public, save  :: Ra_ref_i
    real, public, save  :: Ra_ref
    real, public, save  :: Ra_O3zR_i
    real, public, save  :: Ra_tar_i

    ! Stomatal conductance/resistance
    real, public, save  :: Gsto     ! Mean O3 conductance
    real, public, save  :: Rsto     ! Mean O3 resistance (s/m)
    real, public, save  :: Gsto_l   ! Single leaf O3 conductance
    real, public, save  :: Rsto_l   ! Single leaf O3 resistance (s/m)
    real, public, save  :: Gsto_c   ! Canopy O3 conductance
    real, public, save  :: Rsto_c   ! Canopy O3 resistance (s/m)
    real, public, save  :: Gsto_PEt ! Potential canopy O3 conductance (for PEt)
    real, public, save  :: Rsto_PEt ! Potential canopy O3 resistance (for PEt)

    ! O3
    real, public, save :: O3_ppb_i      ! O3 concentration at izR (ppb)
    real, public, save :: O3_ppb        ! O3 concentration at canopy (ppb)
    real, public, save :: O3_nmol_m3    ! O3 concentration at canopy (nmol/m^3)
    real, public, save :: Vd            ! Deposition velocity at canopy (m/s)
    real, public, save :: Vd_i          ! Deposition velocity at izR (m/s)
    real, public, save :: Ftot          ! Total O3 flux
    real, public, save :: Fst           ! Upper leaf stomatal flux
    real, public, save :: AFst0         ! Accumulated Fst
    real, public, save :: AFstY         ! Accumulated Fst over threshold Y
    real, public, save :: OT40          ! OT40 (canopy)
    real, public, save :: AOT40         ! Accumulated OT40 (canopy)
    real, public, save :: OT0           ! OT with no threshold (upper leaf)
    real, public, save :: AOT0          ! Accumulated OT0 (upper leaf)
    real, public, save :: fO3

end module Variables

