module Radiation_ml

!================== Now under CVS control =================
! $Author: mifads $
! $Id: Radiation_ml.f90,v 1.2 2002/09/12 14:51:08 mifads Exp $
! $Name:  $
! =========================================================

  use PhysicalConstants_ml  , only: PI, DEG2RAD, RAD2DEG
  implicit none
  private

  !/ Subroutines:
  public :: ZenAng         ! => coszen=cos(zen), zen=zenith angle (degrees) 
  public :: ClearSkyRadn   ! => irradiance (W/m2), clear-sky
  public :: CloudAtten     ! => Cloud-Attenuation factor
  public :: CanopyPAR      ! => sun & shade PAR  values, and LAIsunfrac

  !/ Functions:
  public :: daytime        ! true if zen < 89.9 deg


  real, public, save :: solar       ! => irradiance (W/m^2)
  real, public, save :: Idrctn      ! => irradiance (W/m^2), normal to beam
  real, public, save :: Idfuse      ! => diffuse solar radiation (W/m^2)
  real, public, save :: Idrctt      ! => total direct solar radiation (W/m^2)
  
  real, public, save :: zen         !   Zenith angle (degrees)
  real, public, save :: coszen      ! = cos(zen) 
                                    ! (= sinB, where B is elevation angle)

 ! Canopy associated values:
 !real, public, save :: LAIsunfrac   ! sun-fraction of LAI
 !real, public, save :: PARsun       ! sun-leaf PAR
 !real, public, save :: PARshade     ! shade-leaf PAR

  real, public, parameter :: &
      PARfrac = 0.45,   & ! approximation to fraction (0.45 to 0.5) of total 
                          ! radiation in PAR waveband (400-700nm)
      Wm2_uE  = 4.57,   & ! converts from W/m^2 to umol/m^2/s
      Wm2_2uEPAR= PARfrac * Wm2_uE  ! converts from W/m^2 to umol/m^2/s PAR

  logical, private, parameter :: DEBUG = .true.

  contains

  ! ======================================================================
 subroutine ZenAng(lon, lat, daynr, nydays, hr)
  ! ======================================================================
  !  routine determines (approximate) cos(zen), where "zen" denotes the zenith 
  !  angle, (in accordance with Iversen and Nordeng (1987, p.28))
  !  dnmi  29-9-95  Hugo Jakobsen, modified Dave, 2002-2004
  !
  ! arguments:              
    real,    intent(in) ::  lon      ! longitude (degrees), east is positive
    real,    intent(in) ::  lat      ! latitude (degrees), north is positive
    integer, intent(in) ::  daynr    ! day nr. (1..366)
    integer, intent(in) ::  nydays   ! number of days per year (365 or 366)
    real,    intent(in) ::  hr       ! hour  (0-24, gmt)  ! ds - was integer
    
  ! Caluclates:
  !   zen:         zenith angle (degrees) 
  !   coszen       cos(zen)
  !

  ! ZenAng to be compared with zenith angle routine in UK model
  ! ======================================================================

     !/ Local....
     real    :: lonr, latr, arg, decl, tangle

     lonr=lon*DEG2RAD             ! convert to radians
     latr=lat*DEG2RAD             ! convert to radians

     arg = ((daynr - 80.0)/nydays) * 2.0 * PI  !matches monthly year angle
                                               !calculation in UK model     

     decl = 23.5 * sin(arg) * DEG2RAD     !EMEP procedure for calculating the 
                                          !sun's declination (in radians): 
                                          !differs       
                                          !from the UK procedure (compare)
     
     tangle = lonr + (hr/12.0-1.0)*PI      !no time correction (change?)
     coszen =(sin(decl)*sin(latr)+cos(decl)*cos(latr)*cos(tangle))
     zen = acos(coszen) * RAD2DEG 
  end subroutine ZenAng

  !=============================================================================

  ! Define function for daytime, to keep definitions consistent throughout code.
  ! NB - older code had a check for zen>1.0e-15 --- Why?!

  function daytime(zen) result (day)
       real, intent(in) :: zen    ! Zenith angle (degrees)
       logical :: day
 
       if( zen < 89.9 ) then
            day = .true.
       else
            day = .false.
       end if
  end function daytime

  !=============================================================================
  subroutine ClearSkyRadn(jday,pres)
  !=============================================================================
  !
  !     computes the radiation terms needed for stomatal calculations
  !     one term is computed: total solar radiation (W/m^2)
  !     methodology for this calculation taken from Iqbal, M., 1983,
  !     An introduction to solar radiation, Academic Press, New York, 
  !     pp. 202-210.
  !
  !  history:
  !
  !     From T. Pierce's SolBio code:
  !     Development of this routine was prompted by the need for a
  !     horizontal rather than an actinic flux calculation (which had
  !     been performed by Soleng). Furthermore, Soleng computed total
  !     radiation only out to the near-ir spectrum. This program
  !     is designed only for approximate radiation estimates to be used
  !     for stomatal calculations.
  !
  !     8/90    initial development of SolBio by T. Pierce
  !     95-04    modified by Hugo Jakobsen, 29/9-95  and Dave for EMEP model
  !
  !  argument list description:
  !
      integer, intent(in)  :: jday   ! day no. from 1 Jan (Julian day)
      real,    intent(in)  :: pres   ! surface air pressure 

  ! Calculates clear-sky values of:

    ! solar    total solar radiation, diff.+direct (W/m^2)
    ! Idrctn   direct normal solar radiation (W/m^2)
    ! Idfuse   diffuse solar radiation (W/m^2)
    ! Idrctt   total direct solar radiation (W/m^2)
  !
  !     internal arguments:
  !
  !        cn    - clearness number (defined as the ratio of normal
  !                incident radiation, under local mean water vapour,
  !                divided by the normal incident radiation, for
  !                water vapour in a basic atmosphere)  
  !              - currently, this value set equal to 1.0, but eventually
  !                may vary as a function of latitude and month pending further
  !                literature review.
  !        a     - solar constant at sea-level, varies by day (W/m^2)
  !        aday  - fixed values of a used in the table look up
  !        b     - inverse air mass, varies by day (atm^-1)
  !        bday  - fixed values of b used in the table look up
  !        pres0 - std sea-level pressure (101300 N/m^2)
  !        c     - constant which accounts for water vapour, varies by
  !                Julian day (unitless)
  !        cday  - fixed values of c used in the table look up
  !        iday  - fixed values of Julian day corresponding to aday,
  !                bday and cday
  !        dayinc - day increment used in interpolating between days

  !**********************************************************************
  !     declarations:


  real    ::  a, b, c, dayinc  ! As above
  real :: expa            ! exp. function with zenith angle and air mass
  integer :: i
  integer, dimension(14), save ::   &
       nday = (/  1, 21, 52, 81,112,142,173, 203,234,265,295,326,356,366/)

  real, dimension(14), save ::   &
       aday = (/1203.0,1202.0,1187.0,1164.0,1130.0,1106.0,1092.0,   &
                1093.0,1107.0,1136.0,1136.0,1190.0,1204.0,1203.0/)  &
      ,bday = (/0.141,0.141,0.142,0.149,0.164,0.177,0.185,          &
                0.186,0.182,0.165,0.152,0.144,0.141,0.141/)         &
      ,cday = (/0.103,0.103,0.104,0.109,0.120,0.130,0.137,          &
                0.138,0.134,0.121,0.111,0.106,0.103,0.103/)

  real, save  :: cn = 1.0
  real, save  :: pres0 = 101300.0 


  if ( daytime(zen) ) then  ! night (or too close to 90.0 for comfort)

     ! first, perform the table look up
      do i = 1, 14
        if (jday <=   nday(i)) exit    ! ds go to 20
      end  do

      if ( DEBUG .and. i<1.or.i>14) write(unit=6,fmt=*) "solbio: index err!"

      if (nday(i) == 1) then
        a = aday(1)
        b = bday(1)
        c = cday(1)
      else
        dayinc = real(jday-nday(i-1)) / real(nday(i)-nday(i-1))
        a = aday(i-1) + (aday(i)-aday(i-1))*dayinc
        b = bday(i-1) + (bday(i)-bday(i-1))*dayinc
        c = cday(i-1) + (cday(i)-cday(i-1))*dayinc
      end if

      expa = exp(-b*(pres/pres0)/coszen)

      Idrctn  = cn*a*expa
      Idfuse =  c*Idrctn
      Idrctt  = Idrctn*coszen

      solar  = Idrctt + Idfuse

  else !... Night

     solar = 0.0
     Idrctn = 0.0
     Idfuse = 0.0
     Idrctt = 0.0
     return  !  Nothing else to do!

  end if ! daylight

  end subroutine ClearSkyRadn
!===========================================================================
  subroutine CloudAtten(cl,a,b,c)
    ! Routine applies a cloud-attenuation factor to arguments, which could
    ! be say, Idrctt,Idfuse,solar, or just solar: the last 2 arguments are
    ! optional

    ! Agument
      real, intent(in)  :: cl               ! cloud fraction   (0-1)
      real, intent(inout)           :: a     
      real, intent(inout), optional :: b,c

      real :: f           ! cloud attenuation factor

      f = 1.0 - 0.75*cl**3.4     !(source: Kasten & Czeplak (1980)) 

      a = a * f

      if( present(b) ) b = b * f
      if( present(c) ) c = c * f

  end subroutine CloudAtten

!===========================================================================
    subroutine CanopyPAR(LAI,albedo,PARsun,PARshade,LAIsunfrac)
!===========================================================================
!
!    Calculates g_light, using methodology as described in Emberson et 
!    al. (1998), eqns. 31-35, based upon sun/shade method of Norman (1979,1982)

!     input arguments:

    real, intent(in)  :: LAI       ! leaf area index (m^2/m^2), one-sided
    real, intent(in)  :: albedo    ! Fraction, 0-1
    real, intent(out) :: PARsun, PARshade
    real, intent(out) :: LAIsunfrac


!     internal variables:

    real :: sinB      ! B = solar elevation angle  = complement of zenith angle
    real :: LAIsun    ! sunlit LAI

    real, parameter :: cosA    = 0.5   ! A = mean leaf inclination (60 deg.), 
     ! where it is assumed that leaf inclination has a spherical distribution


    sinB = coszen  ! = cos(zen)

    LAIsun = (1.0 - exp(-0.5*LAI/sinB) ) * sinB/cosA
    LAIsunfrac = LAIsun/LAI

! PAR flux densities evaluated using method of
! Norman (1982, p.79): 
! "conceptually, 0.07 represents a scattering coefficient"  

    PARshade = Idfuse * exp(-0.5*LAI**0.7) +  &
               0.07 * Idrctt  * (1.1-0.1*LAI)*exp(-sinB)   

    PARsun = Idrctt *cosA/sinB + PARshade

!.. Convert units, and to PAR fraction
!.. and multiply by albedo

    PARshade = PARshade * Wm2_2uEPAR * ( 1.0 - albedo )
    PARsun   = PARsun   * Wm2_2uEPAR * ( 1.0 - albedo )

  end subroutine CanopyPAR

!--------------------------------------------------------------------
!===============================================================
end module Radiation_ml
!===============================================================
