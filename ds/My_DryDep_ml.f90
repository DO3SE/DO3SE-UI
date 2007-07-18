module My_DryDep_ml

! =========================================================
!  Specifies which of the possible species (from Wesely's list)
!  are required in the current air pollution model   
! =========================================================

  use Wesely_ml
  implicit none
  private

  !/** Variables used in deposition calculations
 
  ! DDEP_xx gives the index that will be used in the EMEP model
  ! WES_xx gives the index of the Wesely gas to which this corresponds

  ! Here we define the minimum set of species which has different
  ! deposition velocities. We calculate Vg for these, and then
  ! in the full EMEP model we can use the rates for other similar species. 
  ! (e.g. AMSU can use the Vg for SO4.  Must set NDRYDEP_CALC species

  !/** IMPORTANT: the variables below must match up in the sense that, for 
  ! example, if DDEP_NH3=4 then the 4th element of DRYDEP must be WES_NH3.

  !/** Outputs fix - for the box-model, the last species specified will
  !    have extra outputs. Here it is ozone.


  integer, public, parameter :: NDRYDEP_CALC = 1

  integer, public, parameter :: &
      DDEP_O3  =  1, &
      DDEP_NH3 = -1                    !Dummy value
      ! DDEP_HNO3 = 1, DDEP_NO2 = 5, DDEP_SO2 = 2  &
      !,DDEP_NH3  = 4, DDEP_O3  = 3
 
  integer, public, parameter, dimension(NDRYDEP_CALC) :: &
       DRYDEP_CALC = (/ WES_O3 /)
      !DRYDEP_CALC = (/ WES_HNO3, WES_SO2, WES_O3, WES_NH3, WES_NO2 /)

  !/** Compensation pount approach from CEH used?:
  ! default is false for now, as the validity over 50km grids needs to
  ! be tested.

  logical, public, parameter :: COMPENSATION_PT = .false.   ! default


! **sc: characters for printout which is generated directly from Rsurface 
!        module or the program test_dep

  character(len=*), public, parameter, dimension(NDRYDEP_CALC) :: & 
      GASNAME = (/ "    O3" /)
      !GASNAME = (/ "  HNO3", "   SO2", "    O3", &
      !             "   NH3", "   NO2" /)
  
      
       
  end module My_DryDep_ml
