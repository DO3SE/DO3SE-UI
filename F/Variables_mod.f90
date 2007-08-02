!*******************************************************************************
! Variables_mod.f90 - Global variables module
!
! Contains all variables used in more than one part of the model
!*******************************************************************************

module Variables_mod
    
    ! Outputs for canopy level
    real, public, save :: Ra
    real, public, save :: Rb
    real, public, save :: Rsur
    real, public, save :: Rsto
    real, public, save :: Gsto
    real, public, save :: Vg
    real, public, save :: Ftot
    real, public, save :: Fns
    real, public, save :: Fstom

    ! Outputs for leaf level
    real, public, save :: Fst
    real, public, save :: AFstY
    real, public, save :: Yield_Loss
    real, public, save :: AOT40

    ! Day of year for previous dataset
    integer, public, save :: dd_prev = -1

end module Variables_mod

