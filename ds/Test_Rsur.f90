program test_Rsur 

  !/  Small prog to test Radiation and Gsto modules.
  !/  (Extension of Test_Gsto.f90)
  !

  use My_DryDep_ml,      only : NDRYDEP_CALC
  use LandClasses_ml,    only : landuse, WHEAT
  use Gsto_ml,           only : Init_Gsto, f_phen, g_sto, g_sun
  use LocalVariables_ml, only : LAI, SAI, hveg, &
                                PARsun, PARshade, LAIsunfrac,Ts_C, so2nh3ratio, &
                                rh,vpd,SWP,ustar, snow
  use Radiation_ml,      only : &
       ZenAng, zen, daytime                         &! Zenith angle terms 
      ,ClearSkyRadn, Idrctt,Idfuse, CloudAtten      &! Radiation terms
      ,CanopyPAR                               ! PAR terms for specific landuse
  use Rb_ml,             only : Rb_gases
  use Rsurface_ml,       only : Rsurface
  use Phenology_ml,      only : Init_phenology, Growing_season, Phenology
  implicit none

  character(len=80) :: errmsg = "ok"
  logical, parameter :: debug_flag = .true.
  integer :: day_of_year, nydays, hr
  integer :: SGS, EGS    ! start and end of growing season
  real    :: pressure, latitude, longitude, cloud
  real    :: cms = 100.0   ! convert m/s to cm/s
  real, dimension(NDRYDEP_CALC) :: Rsur_wet, Rsur_dry, Rb


  integer :: lu=WHEAT   ! Fake-wheat, for now


  !/ Some test values.............

   Ts_C       = 22.0 ! degrees C
   f_phen     = 1.0      !only needs calculating once per day, so do outside
   vpd        = 0.0
   rh         = 0.6
   swp        = 0.0
   snow       = 0
   ustar      = 0.5
   so2nh3ratio = 10.0

   pressure        = 1.0e5  !Pa
   cloud           =   0.1
   latitude        =  52.0
   longitude       =   2.0
   day_of_year     = 180    !mid-summer
   nydays          = 365     !days per year

   errmsg = "ok"

  !/..............................
   call Init_phenology(10,errmsg)
   call Init_Gsto(errmsg)
   call Growing_season(lu,latitude,SGS,EGS)
   print *, "Initialisation ", errmsg
   print *, "For landuse ", landuse(lu)%name

  !/..............................


   call Phenology(day_of_year,lu,SGS,EGS,LAI,SAI,hveg)


  print "(a2,3a7,2a7,3a10,2a12)", "hr", " zen ", "PARsun","PARshd", &
                     "LAI", "SAI", &
                     "Rsur_dry", "Rsur_wet", " Rb ", &
                     "g_sto(cm/s)", "g_sun(cm/s)"
   do hr = 0, 23

       call ZenAng(longitude,latitude,day_of_year,nydays,real(hr))
 
       if ( daytime(zen) ) then

           call ClearSkyRadn(day_of_year,pressure)
           call CloudAtten(cloud,Idrctt,Idfuse)
           call CanopyPAR(LAI,landuse(lu)%albedo,PARsun,PARshade,LAIsunfrac)

       else
           PARsun   = 0.0
           PARshade = 0.0
       end if

       call Rb_gases(landuse(lu)%water,Rb)

       call Rsurface(lu,debug_flag,Rsur_dry,Rsur_wet,errmsg)

       !print *, "Rsur: ", PARsun,Rsur_dry(1), Rsur_wet(1), Rb(1)
       if ( errmsg /= "ok" ) stop

       print "(i2,3f7.1,2f7.1,3f10.3,2f12.4)", hr,  zen, PARsun,PARshade, &
                     LAI, SAI, Rsur_dry(1), Rsur_wet(1), Rb(1), &
                     g_sto * cms, g_sun * cms

   end do
  !/..............................

end program test_Rsur
  
