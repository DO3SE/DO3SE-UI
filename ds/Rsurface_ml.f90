module Rsurface_ml

use CEH_ml,            only : CEH_factors, RgsS_dry, RgsS_wet, humidity_fac, r_water
use Gsto_ml,           only : g_stomatal, g_sto, g_sun
use LandClasses_ml, only : landuse   ! type includes name, Gcalc, forest
                                ! crops, water, b, albedo, RgsS, RgsO

use LocalVariables_ml, only :  Ts_C, rh, LAI, SAI, hveg, ustar, &
                          SWP, snow, PARsun, &
                          so2nh3ratio    ! for CEH module
use My_DryDep_ml, only : NDRYDEP_CALC, & ! no. of Wesely species  used
                         DRYDEP_CALC    ! array with species which are needed
                    
!Step3 use SoilWater_ml, only : SWP
use Wesely_ml, only  : Wesely_tab2, & ! Wesely Table 2 for 14 gases
                       WES_HNO3,    & ! indices to identify HNO3
                       WES_NH3,     & ! indices to identify NH3  
                       DRx            !  Ratio of diffusivities to ozone
implicit none
private

public   ::  Rsurface

logical, private, parameter :: MY_DEBUG = .true.

 
    
contains
! =======================================================================


  subroutine Rsurface(lu,debug_flag,Rsur_dry,Rsur_wet,errmsg) 
! =======================================================================
!
!     Description
!       calculates bulk surface resistance (Rsur) for all required gases.
!
!       For O3 the methodology is derived from EMEP MSC_W Note 6/00; the 
!       following pathways apply for the surface resistance for O3:
!
!        -- Rinc-- Rgs      In-canopy + soil/ground cover
!       |
!       |
!        -------- Rext      cuticular+other external surface
!       |
!       |
!        -------- Rsto      Stomatal

!     Hence, we have a surface conductance: 
!
!       Gsur =      LAI +  SAI  +       1
!                   ___    ___     ____________
!                   Rsto   Rext    Rinc + Rgs
!
!     For SO2 and NH3 we use the CEH suggestion of a simple non-stomatal
!     uptake (which is stringly affected by wetness/RH):
!
!        -------- Rns       Non-stomatal
!       |
!        -------- Rsto      Stomatal
!
!     [ Note that the O3 formulation can be written in the same way when we
!     define GnsO = SOA/Rext + 1/(Rinc+Rgs) ]
!
!     Hence, for all gases, we have a surface conductance: 
!
!       Gsur =      LAI * Gsto  +  Gns

!  Wesely's method for other gases was based upon deriving resistances for 
!  ozone and SO2 first (e.g. RgsO, RgsS for Rgs) and then scaling using
!  effective Henry coefficients (H*) and reactivity coefficients (f0) for
!  each gas. However, here we apply scaling to Gns, not individual resistances.
!
! Structure of routine
!
!  1. Calculate:
!        Rlow             low-temperature correction
!        Rinc             in-canopy resistance
!        Rsur(HNO3)  
!        Gsto(O3)         stomatal conductance (if LAI > 0)
!
!       FOR EACH remaining gas (icmp is used as an index, since cmp is assumed 
!                               to  abbreviate "component".):
!  2. Calculate ground surface resistance, Rgs
!              if (LAI<0.1) go to 4  (for snow/ice/water...)
!  3. if (LAI>0.1)  calculate Gext
!  4. Calculate Rsur(icmp)
!       END
!
! =======================================================================

!......................................
! Input:

    integer, intent(in) :: lu           ! land-use index
    logical, intent(in) :: debug_flag   ! set true if output wanted 
                                        ! for this location

! Output:

   real,dimension(:),intent(out) :: Rsur_dry   !  Rs  for dry surfaces 
   real,dimension(:),intent(out) :: Rsur_wet   !  Rs  for wet surfaces
   character(len=*), intent(out) :: errmsg


 ! external resistance for Ozone
  real, parameter :: &
        RextO =  2500.0    ! prelim. value - gives Gext=0.2 cm/s for LAI=5


! Here, "Gext=0.2cm/s" refers to the external conductance, G_ext, where 
! G_ext=LAI/R_ext. In many studies, it has been assumed 
! that G_ext should be low, particularly relative to stomatal conductance g_s.
! Results from a variety of experiments, however, have made the above 
! estimates  Rext0 and RextS plausible.  The above equation for G_ext has been
! designed on the basis of these experimental results. 

! Notice also that given the equations for the canopy resistance R_sur and the 
! deposition velocity V_g, V_g>=LAI/R_ext. The value of G_ext can therefore be
! interpreted as the minimum value for V_g.


! Working values:
   
    integer :: icmp             ! gaseous species
    integer :: iwes             ! gaseous species, Wesely tables
    logical :: canopy,        & ! For SAI>0, .e.g grass, forest, also in winter
         leafy_canopy           ! For LAI>0, only when green
    real, parameter :: SMALLSAI= 0.05  ! arbitrary value but small enough
    real :: Hstar, f0           ! Wesely tabulated Henry's coeff.'s, reactivity
    real :: Rlow                ! adjustment for low temperatures (Wesely,
                                ! 1989, p.1296, left column) 
    real :: Rinc                ! In-canopy adjustment
    real :: xRgsO        ! see  DepVariables_ml
    real :: Rgs_dry, Rgs_wet    !  

    real :: GnsO, GnsS_dry, GnsS_wet, Gns_dry, Gns_wet


! START OF PROGRAMME: 

  !===========================================================================
  !/**  Adjustment for low temperatures (Wesely, 1989, p.1296, left column)

    Rlow = 1000.0*exp(-Ts_C - 4.0)

  !===========================================================================
  !/** get CEH humidity factor and RgsS_dry and RgsS_wet:

    call CEH_factors(so2nh3ratio,Ts_C,rh,landuse(lu)%forest)



!##############   1. Calculate In-Canopy Resistance, Rinc    ################

    canopy       = ( SAI     > SMALLSAI ) ! - can include grass
    leafy_canopy = ( LAI     > SMALLSAI ) ! - can include grass

  !/** For canopies:
  !/** Calculate stomatal conductance if daytime and LAI > 0

   if( leafy_canopy  .and. PARsun > 0.001 ) then  ! Daytime 

        call g_stomatal(debug_flag,lu)
   else
        g_sun = 0.0
        g_sto = 0.0

   end if ! leafy canopy and daytime


  !/** Calculate Rinc, Gext 
  !NB-    previous if-test for snow replaced by more efficient
  !       multiplication, since snow=0 or 1.

   if(  canopy ) then   

         Rinc = landuse(lu)%b  * SAI * hveg  / ustar    ! Erisman's b.LAI.h/u*

         RgsS_dry = RgsS_dry  + Rlow  + snow * 2000.0
         RgsS_wet = RgsS_wet  + Rlow  + snow * 2000.0

        ! for now, use CEH stuff for canopies, keep Ggs for non-canopy

         GnsS_dry = 1.0 /  RgsS_dry       ! For SO2, dry, low NH3 region
         GnsS_wet = 1.0 /  RgsS_wet   ! For SO2, wet, low NH3 region

   else   ! No canopy present

        Rinc = 0.0

        !/ Here we preserve the values from the ukdep_gfac table
        !  giving higher deposition to water, less to deserts

        RgsS_dry = landuse(lu)%RgsS + Rlow  + snow * 2000.0
        RgsS_wet = RgsS_dry    ! Hard to know what's best here
      
   end if !  canopy


!####   2. Calculate Surface Resistance, Rsur, for HNO3 and Ground Surface 
!####      Resistance, Rgs, for the remaining Gases of Interest                                

   !/ Ozone values....

     xRgsO  = landuse(lu)%RgsO + Rlow  + snow *    0.0 !BUG!! QUERY??? ?? BUG???
     GnsO   = SAI/RextO + 1.0/( xRgsO + Rinc ) ! (SAI=0 if no canopy)


!.........  Loop over all required gases   ................................

  GASLOOP: do icmp = 1, NDRYDEP_CALC
      iwes = DRYDEP_CALC(icmp)

     !-------------------------------------------------------------------------

     !  code obtained from Wesely during 1994 personal communication
     !  but changed (ds) to allow Vg(HNO3) to exceed Vg(SO2)

        if ( iwes == WES_HNO3 ) then
            Rsur_dry(icmp)  = max(1.0,Rlow)
            Rsur_wet(icmp)  = Rsur_dry(icmp)
            cycle GASLOOP
        end if

     !-------------------------------------------------------------------------
     ! Calculate the Wesely variables Hstar (solubility) and f0 (reactivity)

        Hstar =Wesely_tab2(2,iwes)    !Extract H*'s 
        f0    =Wesely_tab2(5,iwes)    !Extract f0's
    
     !-------------------------------------------------------------------------

                          

     !   Use SAI to test for snow, ice, water, urban ...

       if ( canopy  ) then   

         ! ###   3. Calculate Cuticle conductance, Gext   ################
         ! ###      and  Ground surface conductance Ggs:

         ! Corrected for other species using Wesely's eqn. 7 approach. 
         ! (We identify leaf surface resistance with Rext/SAI.)
         ! but for conductances, not resistances (pragmatic, I know!)



         ! ##############   4. Calculate Rsur for canopies   ###############


           if ( DRYDEP_CALC(icmp) == WES_NH3 ) then

             Gns_dry = 1.0/r_water               !/** r_water  from CEH_ml
             Gns_wet =  Gns_dry

           else  ! Not NH3

               Gns_dry = 1.0e-5*Hstar*GnsS_dry + f0 * GnsO   ! OLD SO2!
               Gns_wet = 1.0e-5*Hstar*GnsS_wet + f0 * GnsO 

               !.. and allow for partially wet surfaces at high RH, even for Gns_dry

               Gns_dry = Gns_dry * (1.0-humidity_fac) + Gns_wet * humidity_fac

           end if  ! NH3 test

           Rsur_dry(icmp) = 1.0/( LAI*DRx(iwes) *g_sto + Gns_dry  )
           Rsur_wet(icmp) = 1.0/( LAI*DRx(iwes) *g_sto + Gns_wet  )


       else   ! Non-Canopy modelling:

           Rgs_dry = 1.0/(1.0e-5*Hstar/RgsS_dry + f0/xRgsO)  ! Eqn. (9)
           Rgs_wet = 1.0/(1.0e-5*Hstar/RgsS_wet + f0/xRgsO)  ! Eqn. (9)

           Rsur_dry(icmp)   = Rgs_dry
           Rsur_wet(icmp)   = Rgs_wet

           !BUG in EMEP??  Rsur_wet(icmp)   = Rgs   !!?? BUG ??!

       end if  ! end of canopy tests 

  end do GASLOOP

 end subroutine Rsurface

!--------------------------------------------------------------------

end module Rsurface_ml
