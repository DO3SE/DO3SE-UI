!QUERY: Should needle-age be included in g_sun?
!QUERY: phenology for fake_wheat

module Gsto_ml
  use LandClasses_ml,    only : NLANDUSE, landuse
  use LocalVariables_ml, only : Ts_C, vpd, SWP, PARsun, PARshade, LAIsunfrac
  implicit none
  private

! DESCRIPTION:
! Module containing main variables and parameters associated with the
! stomatal conductance module of Emberson et al. (EMEP Rep. 6/01).
! Notation now consistent with 2004 Mapping Manual.



  !/--------- Subroutines --------------------------------------------------

  public :: Init_Gsto       !- Reads in f-factors, Initialises
  public :: g_stomatal      !- produces g_sto and g_sun

  private :: get_f_light     !-
  private :: Conif_fphen    !-  correction for old needles

  !/--------- Variables available from this module -----------------------

  real, public, save  :: &
          g_sto          & ! stomatal conductance (m/s)
       ,  g_sun            ! g_sto for upper-canopy sun-leaves


  real, public, save :: & !/ g_sto factors (0-1):
        f_phen     &            ! phenology (age)
       ,f_temp     &            ! temperature
       ,f_vpd      &            ! vapour pressure deficit
       ,f_light    &            ! light
       ,f_swp                   ! soil water potential


type, private :: gf    
   character(len=3) :: code   ! 2-3-letter name
   real ::  g_max          ! max. value conductance (UNITS)
   real ::  f_min          ! min. value Conductance f_s
   real ::  f_lightfac     ! light coefficient 
  ! Temperature
   real ::  T_min          ! temperature when f_temp starts
   real ::  T_opt          ! temperature when f_temp max.   
   real ::  T_max          ! temperature when f_temp stops  
  ! Phenology terms:
   real ::  f_phen_min     ! min. value of f_phen
   real ::  Sf_phenlen     ! length in days from f_phen=f_min to f_phen=1
   real ::  Ef_phenlen     ! length in days from f_phen=1 to f_phen=f_phen_min
  ! VPD:
   real ::  VPD_max        ! threshold VPD when relative g = f_min
   real ::  VPD_min        ! threshold VPD when relative g = 1
  ! SWP:
   real ::  SWP_max        ! threshold SWP when relative g = 1
   real ::  PWP            ! threshold SWP when relative g = f_min
                           ! and assumed equal to permanent wilting point
end type gf
    
type(gf), private, parameter, dimension(NLANDUSE) :: g =(/ &
! g_sto  variables read previously from Gsto_inputs.dat   ................
!------------------------------------------------------------------------------
!   LU     gmax  fmin flight     ftemp   fphe Sfphen Efphen   fVDP          fSWP
!                            min opt max min  len   len   max    min    SWPmax  PWP   
!------------------------------------------------------------------------------
 gf("CF ",160,  0.1  ,0.0083,  1,18,36,  0.2, 130, 130,  0.6  , 3.3,  -0.76, -1.2   ) &
,gf("DF ",134,  0.13 ,0.006 , -5,22,35,  0.3,  50,  50,  0.93 , 3.4,  -0.55, -1.3   ) &
,gf("NF ",180,  0.13 ,0.013 ,  4,20,37,  0.3, 110, 150,  0.4  , 1.6,  -0.4 , -1     ) &
,gf("BF ",200,  0.03 ,0.009 ,  4,20,37,  0.3, 110, 150,  1.8  , 2.8,  -1.1 , -2.8   ) &
,gf("WH ",450,  0.01 ,0.009 , 12,26,40,  0.1,   0,  45,  0.9  , 2.8,  -0.3 , -1.1   ) &
,gf("TC ",300,  0.01 ,0.009 , 12,26,40,  0.1,   0,  45,  0.9  , 2.8,  -0.3 , -1.1   ) &
,gf("MC ",156,  0.019,0.0048,  0,25,51,  0.1,   0,  45,  1.0  , 2.5,  -0.11, -0.8   ) &
,gf("RC ",360,  0.02 ,0.0023,  8,24,50,  0.2,  20,  45,  0.31 , 2.7,  -0.44, -1.0   ) &
,gf("SNL", 60,  0.01 ,0.009 ,  1,18,36,  0.1,   0,  45, 88.8  ,99.9,  -9.99 ,-99.0 ) &
,gf("FWH",450,  0.01 ,0.009 , 12,26,40,  0.1,   0,  45,  0.9  , 2.8,  -0.3 , -1.1   ) &
,gf("GR ",270,  0.01 ,0.009 , 12,26,40,  1.0,   0,   0,  1.3  , 3.0,  -0.49, -1.5   ) &
,gf("MS ",213,  0.14 ,0.012 ,  4,20,37,  0.2, 130, 130,  1.3  , 3.0,  -1.1 , -3.1   ) &
,gf("WE ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) &
,gf("TU ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) &
,gf("DE ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) &
,gf("W  ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) &
,gf("I  ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) &
,gf("U  ", -1,   -1  ,  -1  , -1,-1,-1,  0.0,   0,  -1,   -1  , -1 ,   -1  , -99   ) /)
!------------------------------------------------------------------------------
!Notes: Basis was Emberson et al, EMEP Report 6/2000
!Numbers and notation updated to Mapping Manual, 2004 and changes recommended
!in Tuovinen et al, 2004
!
!WH = wheat
!TC = mixed temperate crops, with lower gmax, for EMEP-scale modelling
!#SG  270   0.1   0.009   12 26 40   1.0    0     0    1.3    3.0   -0.49  -1.5   
contains
!..............................................................................

!=======================================================================
    subroutine Init_Gsto(errmsg)
!=======================================================================
       character(len=*), intent(inout) :: errmsg
       integer :: lu
       errmsg = "ok"
       do lu = 1, NLANDUSE
         if( g(lu)%code /= landuse(lu)%code ) then
               errmsg = "Gsto Code mismatch!!" // g(lu)%code
         end if
       end do
    end subroutine Init_Gsto
!=======================================================================

    subroutine g_stomatal(debug_flag,lu)
!=======================================================================

!    Calculates stomatal conductance g_sto based upon methodology from 
!    EMEP MSC-W Note 6/00 and Mapping Manual (2004):
!
!TODO: change 41000 for real conversion
!    g_sto = [g_max * f_pot * f_light * f_temp * f_vpd * f_swp ]/41000.0
!
! Inputs:

  logical, intent(in) :: debug_flag   ! set true if output wanted 
  integer, intent(in) :: lu           ! land-use index (max = nlu)
!  real, intent(in) :: coszen          ! cos of zenith angle
!  real, intent(in) :: Idfuse          ! Diffuse radiation
!  real, intent(in) :: Idrctt          ! Direct  radiation
!  real, intent(in) :: Ts_C            ! surface temp. at height 2m (deg. C)
!  real, intent(in) :: pres            ! surface  pressure (Pa) 
!  real, intent(in) :: vpd             ! vapour pressure deficit (kPa)
!  real, intent(in) :: SWP             ! soil water potential (MPa)

! Outputs:
!    g_sto, g_sun       ! stomatal conductance for canopy and sun-leaves

  real :: f_sun                   ! light-factor for upper-canopy sun-leaves
  real :: f_env                   ! product of environmental f factors
  real :: dg, dTs, bt             ! for temperate calculation


        
!..1 ) Calculate f_pot. Max value is 1.0.
!---------------------------------------
! - these calculations only needed once per day - best done outside
!        LAI calculations
!        Subroutine Conif_fphen still kept in this module though.
!... 


!..2 ) Calculate f_light 
!---------------------------------------
 ! (n.b. subroutine get_f_light is defined below)
 ! gsun is here the light factor. Used as g_sto(sun) later

  !call get_f_light(coszen,Idrctt,Idfuse,f_lightfac(lu),LAI, f_sun, f_light)    
  call get_f_light(g(lu)%f_lightfac, f_sun, f_light)    
  

!..3) Calculate  f_temp
!---------------------------------------
! Asymmetric  function from Mapping Manual
! NB _ much more efficient to tabulate this - do later!
  
  dg  =    ( g(lu)%T_opt - g(lu)%T_min )
  bt  =    ( g(lu)%T_max - g(lu)%T_opt ) / dg
  dTs = max( g(lu)%T_max - Ts_C, 0.0 )      !CHECK why max?
  f_temp = dTs / ( g(lu)%T_max - g(lu)%T_opt )
  f_temp = ( Ts_C - g(lu)%T_min ) / dg *  f_temp**bt


  f_temp = max(f_temp,g(lu)%f_min )


!..4) Calculate f_vpd
!---------------------------------------

 f_vpd = g(lu)%f_min + (1.0-g(lu)%f_min) * (g(lu)%VPD_min - vpd )/ &
                                           (g(lu)%VPD_min - g(lu)%VPD_max )
 f_vpd = min(f_vpd, 1.0)
 f_vpd = max(f_vpd, g(lu)%f_min)


!..5) Calculate f_swp
!---------------------------------------

  !/  Use SWP_Mpa to get f_swp. We just need this updated
  !   once per day, but for simplicity we do it every time-step.

       f_swp = g(lu)%f_min+(1-g(lu)%f_min)*(g(lu)%PWP-SWP)/(g(lu)%PWP-g(lu)%SWP_max)
       f_swp = min(1.0,f_swp)


!.. And finally,
!---------------------------------------
! (using factor 41000 from mmol O3/m2/s to s/m given in Jones, App. 3
!  for 20 deg.C )

   f_env = f_temp * f_vpd * f_swp
   f_env = max( f_env,g(lu)%f_min )
   f_env = f_phen * f_env /41000.0

   g_sun = g(lu)%g_max * f_sun   * f_env       ! f_sto for sunlit part
   g_sto = g(lu)%g_max * f_light * f_env       ! f_sto for whole canopy 

  end subroutine g_stomatal

!===========================================================================
    subroutine get_f_light(f_lightfac,f_sun,f_light)
!===========================================================================
!
!    Calculates f_light, using methodology as described in Emberson et 
!    al. (1998), eqns. 31-35, based upon sun/shade method of  
!    Norman (1979,1982)

! Arguments:

    real, intent(in)  :: f_lightfac ! land-use specific light factor
    real, intent(out) :: f_sun    ! sun-leaf f_light
    real, intent(out) :: f_light  ! canopy average f_light    

!     internal variables:
    
    real :: f_shade  ! shade-leaf contribution to f_light

    f_sun   = (1.0 - exp (-f_lightfac*PARsun  ) ) 
    f_shade = (1.0 - exp (-f_lightfac*PARshade) ) 

    f_light = LAIsunfrac * f_sun + (1.0 - LAIsunfrac) * f_shade

  end subroutine get_f_light

!--------------------------------------------------------------------

    !=======================================================================
    subroutine Conif_fphen(imm,f_phen)
    ! =====================================================================
    !   modifies f_phen for effect of older needles, with the simple
    !   assumption that f_phen(old) = 0.5.
    !
   !/ arguments

    integer, intent(in) :: imm    ! month
    real,   intent(inout) :: f_phen   ! Requires initial input of f_phen
                                      ! (once obtained as output from g_stomatal)

   !/ Some parameters:
   !  Proportion of needles which are from current year:
    real, parameter, dimension(12) :: Pc = (/  &
                   0.53, 0.535, 0.54, 0.545, 0.1, 0.15,  &
                   0.27,  0.36, 0.42,  0.48, 0.5,  0.5  /)

    real, parameter :: F_POTOLD = 0.5  ! value of f_phen for old needles


!needles from current year assumed to have f_phen as evaluated above;
!needles from previous years assumed to have f_phen of 0.5
!The sum of the f_phen's for the current year is added to the sum of the
!f_phen's for previous years to obtain the overall f_phen for the landuse 
!category temp. conif. forests.

    f_phen = Pc(imm)*f_phen + (1.0-Pc(imm))*F_POTOLD

  end subroutine Conif_fphen
! =====================================================================

end module Gsto_ml
