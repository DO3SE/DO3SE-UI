module LandClasses_ml
implicit none
!=============================================================================
! This module defines the basics landuse data features.
! The list given below can be changed, extended or reduced, but then other
! input data files (Gsto_inputs.dat, UKphenology_inputs.dat) need to be 
! changed for consistency.
! 
! So far, 17 land-use classes are defined. The classes temperate orchard
! and Mediterranean orchard may be added later.

! Step2: albedo values now as fraction
! Phen: landuse defined as parameter, Init subroutine now unecessary
!       Separate WH and FWH categories defined - the latter for EMEP flux

 integer, public, parameter :: NLANDUSE =   18 !number of land-use classes
 integer, public, parameter :: WHEAT    =   10 !land-use class for fake-wheat

 type, public :: land_class
    character(len=3)  :: code
    character(len=13) :: name
    logical           :: Gcalc   ! calculate Gsto?  Set F for bulk Rs
    logical           :: forest  ! 
    logical           :: crops   !
    logical           :: water   !
    real              :: b       ! in-canopy resistance factor
    real              :: albedo  ! fraction
    real              :: RgsS    ! 
    real              :: RgsO    ! 
  end type land_class

 logical, private, parameter :: T = .true., F = .false.   
 type(land_class), public, dimension(NLANDUSE), parameter :: landuse =   &
!
!-----------------------------------------------------------------------------
!               code    name            G  F  C  W   b  Alb Ground Rs:
!                                                           RgsS   RgsO      
!-----------------------------------------------------------------------------
   (/land_class("CF " ,"temp_conif   ", T, T, F, F, 14,0.12, 500, 200 ) &
    ,land_class("DF " ,"temp_decid   ", T, T, F, F, 14,0.16, 500, 200 ) &
    ,land_class("NF " ,"med_needle   ", T, T, F, F, 14,0.12, 500, 200 ) &
    ,land_class("BF " ,"med_broadleaf", T, T, F, F, 14,0.16, 500, 200 ) &
    ,land_class("WH " ,"wheat        ", T, F, T, F, 14,0.20, 150, 200 ) &
    ,land_class("TC " ,"temp_crop    ", T, F, T, F, 14,0.20, 150, 200 ) &
    ,land_class("MC " ,"med_crop     ", T, F, T, F, 14,0.20, 150, 200 ) &
    ,land_class("RC " ,"root_crop    ", T, F, T, F, 14,0.20, 150, 200 ) &
    ,land_class("SNL" ,"moorland     ", T, F, F, F, 14,0.14, 500,1000 ) &
    ,land_class("FWH" ,"flux_wheat   ", T, F, F, F, 14,0.20, 150, 200 ) & !!!
    ,land_class("GR " ,"grass        ", T, F, F, F,  0,0.20, 350,1000 ) &
    ,land_class("MS " ,"med_scrub    ", T, F, F, F,  0,0.20, 500, 200 ) &
!
! Bulk land-covers:
    ,land_class("WE " ,"wetlands     ", F, F, F, F,  0,0.14,  50, 400 ) &
    ,land_class("TU " ,"tundra       ", F, F, F, F,  0,0.15, 500, 400 ) &
    ,land_class("DE " ,"desert       ", F, F, F, F,  0,0.25,1000,2000 ) &
    ,land_class("W  " ,"water        ", F, F, F, T,  0,0.80,   1,2000 ) &
    ,land_class("I  " ,"ice          ", F, F, F, F,  0,0.70, 100,2000 ) &
    ,land_class("U  " ,"urban        ", F, F, F, F,  0,0.18, 400, 400 ) /)
!-----------------------------------------------------------------------------
! Notes:
! Basis was Emberson et al, EMEP Report 6/2000
! Numbers updated to Mapping Manual, 2004 and changes recommended
!  in Tuovinen et al, 2004
!landuse(11)=land_class("SG " ,"shortgrass   ", T, T, F, F,  0, 20, 350,1000 )
!
! flux_wheat is an artificial species with constant LAI, SAI, h throughout year,
! to allow Fst calculations without knowing details of growing season.

end module LandClasses_ml
