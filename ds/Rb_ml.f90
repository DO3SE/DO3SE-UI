module Rb_ml

use LocalVariables_ml, only :  z0, ustar
use My_DryDep_ml, only : NDRYDEP_CALC, & ! no. of Wesely species  used
                         DRYDEP_CALC    ! array with species which are needed
use PhysicalConstants_ml, only : KARMAN
use Wesely_ml, only  : Wesely_tab2, & ! Wesely Table 2 for 14 gases
                       Rb_cor         ! correction factor used in evaluating Rb
implicit none
private

public   ::  Rb_gases

logical, private, parameter :: MY_DEBUG = .true.
    
contains
! =======================================================================
  subroutine Rb_gases(water,Rb) 
! =======================================================================
! Input:

    logical, intent(in) :: water

! Output:

   real,dimension(:),intent(out) :: Rb   ! quasi-laminar boundary layer
                                         ! resistance (s/m)


! Working values:
   
    integer :: icmp             ! gaseous species
    integer :: iwes             ! gaseous species, Wesely tables
    real, parameter :: D_H2O = 0.21e-4  ! Diffusivity of H2O, m2/s
                                        ! From EMEP Notes
    real            :: D_i              ! Diffusivity of gas species, m2/s

  !===========================================================================
 
  GASLOOP: do icmp = 1, NDRYDEP_CALC
      iwes = DRYDEP_CALC(icmp)          ! index in Wesely table
                  
    ! water, sea, rb is calculated as per Hicks and Liss (1976)
      if   ( water ) then

          D_i = D_H2O / Wesely_tab2(1,iwes)

          Rb(icmp) = log( z0 * KARMAN * ustar/ D_i )
          Rb(icmp) = Rb(icmp)/(ustar*KARMAN)

         ! Rb can be very large or even negative from this
         !   formula. We impose limits: (=> min 0.001 m/s, max 0.1 m/s)
         !ToDo:  Limits should be on Vg - see JP discussion


          Rb(icmp) = min( 1000.0, Rb(icmp) ) 
          Rb(icmp) = max(   10.0, Rb(icmp) )

      else 

          Rb(icmp) = 2.0 * Rb_cor(iwes)/(KARMAN*ustar)
      end if

   end do GASLOOP

 end subroutine Rb_gases

!--------------------------------------------------------------------

end module Rb_ml
