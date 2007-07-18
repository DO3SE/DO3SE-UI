module CEH_ml

!================== Now under CVS control =================
  !---------------------------------------------------------------------------
  ! Calculates the acidity and humidity factors used in the EMEP model
  ! deposition (for sulphur) and r_water. 
  !---------------------------------------------------------------------------
  ! For basic reference and methods, see
  !
  ! Unidoc =
  ! EMEP Report 1/2003, Part I. Unified EMEP Model Description.
  !
  ! Also,
  ! RIS: Smith, R.I., Fowler, D., Sutton, M.A., Flechard, C: and Coyle, M.
  !      Atmos. Environ., 34, 3757-3777
  ! + Errata + pers. comm. with R.I.Smith
  !
  ! and
  ! Smith,...... CEH Note
  !---------------------------------------------------------------------------

  implicit none

  public   ::  CEH_factors
  private  ::  Tabulate        ! pre-calculate many values to save CPU
 
  !/** Some parameters for the calculations

  integer, private, parameter :: TMIN = -40, TMAX = 40 ! Allowed temp. range

   real, private, save, dimension(0:100,2) :: tab_humidity_fac
   real, private, save, dimension(0:100)   :: tab_exp_rh  ! For eqn (8.16)
   real, private, save, dimension(0:20) :: &
           tab_acidity_fac,                &
           tab_F2                            ! For Unimod eqn (8.16)


  !/ Calculated values /outputs):
   real, public, save ::  &
        RgsS_dry          &!
       ,RgsS_wet          &!
       ,humidity_fac      &! to interpolate Gns  across different RH
       ,r_water            ! Resistance for NH3 on ground (water) surface

!CEH resistances for SO2 in low NH3 conditions

   real, private, parameter :: CEHd = 180.0, CEHw = 100.0  !  dry, wet, m/s

contains
! =======================================================================

  subroutine CEH_factors( so2nh3ratio, Ts_C, frh, forest)
! =======================================================================
!
! =======================================================================


! Input:
   
   real, intent(in) :: so2nh3ratio    ! so2/nh3 ratio
   real, intent(in) :: Ts_C           ! surface temp. (degrees C)
   real, intent (in):: frh             ! relative humidity (as a fraction)
   logical, intent (in):: forest      ! true if forest


 ! On first call we will tabulate r_water

   logical, save :: my_first_call = .true.

  !local terms governing intermediary calculations in the evaluation of NH3_st:

   real, parameter :: BETA=1.0/22.0   ! Rns factors, see Unimod eqn (8.16)
   real :: F1, F2                     ! Rns factors, see Unimod eqn (8.16)
   real :: a_SN                ! so2/nh3 after correction with 0.6
   integer :: itemp            ! integer Temp in deg.C
   integer :: ia_SN            ! 10*a_SN
   integer :: IRH              ! RH as percent
   real :: acidity_fac  ! to interpolate RgsS between high-low SO2/NH3 ratios 
 
   if ( my_first_call ) then

     call Tabulate()
     my_first_call = .false.

   end if
       
   itemp     =  int( Ts_C + 0.5 )
   itemp     =  max(itemp, TMIN)   ! For safety
   itemp     =  min(itemp, TMAX)   ! For safety

   a_SN  = so2nh3ratio*0.6    !0.6=correction for local nh3
                              ! Unidoc, eqn (8.15) 
   ia_SN = int( 10.0 * a_SN + 0.5 )
   ia_SN = min( 20, ia_SN)
   IRH   = int( 100.0 * frh )

  !/ 1) Acidity factor & Rgs for sulphur:

       acidity_fac = tab_acidity_fac( ia_SN )

       RgsS_dry    = acidity_fac * CEHd
       RgsS_wet    = acidity_fac * CEHw

  !/ 2) Humidity factor:  (F=forest, G=grass+other)

       if( forest ) then
           humidity_fac = tab_humidity_fac(IRH,1) 
       else
           humidity_fac = tab_humidity_fac(IRH,2) 
       end if


  !/ 3) r_water  - see Unimod eqn (8.16)
  !                =RIS eq. (24), modified by CEH Note

    if (Ts_C >0 ) then    ! Use "rh" - now in fraction 0..1.0

           !F1 = 10.0 * log10(Ts_C+2.0) * exp(100.0*(1.0-frh)/7.0)
           F1 = 10.0 * log10(Ts_C+2.0) * tab_exp_rh(IRH)
           F2 = tab_F2( ia_SN  )

           r_water = BETA * F1 * F2
           r_water = min( 200.0, r_water)  ! After discussion with Ron
           r_water = max(  10.0,r_water)

     else if ( Ts_C > -5 ) then

           r_water=200.0
     else

           r_water=1000.0
     end if !Ts_C



 end subroutine CEH_factors

  !=======================================================================

   subroutine Tabulate()
    !/**  Tabulates humidity factors, 

     real :: a_SN
     integer :: IRH, rh_lim, veg, ia_SN
     integer, parameter, dimension(2) :: Rhlim = (/ 85,  75 /)   ! RH limits for F=foerst, G=grass

    tab_humidity_fac(:,:) = 0.0

    ! Acidity factor
     do ia_SN = 1, 20
       a_SN = 0.1 * ia_SN
       tab_acidity_fac( ia_SN )  = exp( -(2.0- a_SN) )
       tab_F2 (ia_SN)            = 10.0**( (-1.1099 * a_SN)+1.6769 )
     end do

     do veg = 1, 2
       rh_lim = Rhlim(veg)
       do IRH = rh_lim, 100
         tab_humidity_fac(IRH,veg) = ( (IRH-rh_lim)/(100-rh_lim) )
       end do
     end do

     do IRH = 0, 100
          tab_exp_rh(IRH) = exp(100.0*(1.0- 0.01*IRH)/7.0)
     end do

   end subroutine Tabulate
  !=======================================================================

end module CEH_ml


