      module PhysicalConstants_ml

! =========================================================
!  Defines Physical constants 
! =========================================================
implicit none

!-- contains no subroutine:


  real , public, parameter ::         &
    ATWAIR = 28.964                   & ! Molecular weight of air (gmol^-1), 
                                        ! Appendix 6 of Jones (1992)
  
  , AVOG   = 6.023e23                 & ! Avogadro's number
  , RGAS_ATML= 0.08205                & ! Molar Gas constant (atm M^-1 K^-1)

  , RGAS_J   = 8.3144                   ! Molar Gas constant (J mol^-1 K^-1)
                                        ! Appendix 6 of Jones (1992) 

                                        ! N.B. ( J = N m^2 = kg m2 s^-2 )
                                        !       M = mol l^-1


real, public, parameter  :: &
       GRAV    = 9.807,           &   ! Gravity  (m s^-2)
       PRANDTL = 0.71,            &   ! Prandtl number (see Garratt, 1992)
       Sc_H20  = 0.6,             &   ! Schmidt number for water
       CP      = 1004.0,          &   ! Specific heat at const. pressure
       R       = 287.0,           &   ! Gas constants J K^-1 kg^-1
       RGAS    = 287.0,           &   ! Gas constants J K^-1 kg^-1
       XKAP    = R/CP,            &
       KARMAN  = 0.4,             &   ! von Karman's constant
                                      ! (=0.35 elsewhere in code!)
       EPSIL   = 1.0e-30,         &   ! may be used as a substitute for zero
                                      ! when one wishes to compare with zero.  
       PI      = 3.14159265358979312000,  &! pi, from 4.0*atan(1.0) on Cray 
                                         !super-computer
       DEG2RAD = PI/180.0,        &   ! Degrees -> Radians
       RAD2DEG = 180.0/PI             ! Radians -> Degrees

  ! CHARNOCK is used to calculate the roughness length for the 
  ! landuse category water

  real, public, parameter  ::    &
    CHARNOCK = 0.032   ! Charnock's alpha:
                       ! see Nordeng (1986), p.31, 
                       ! Nordeng(1991), JGR, 96, no. C4, pp. 7167-7174.
                       ! In the second of these publications, Nordeng uses
                       ! "m" to denote Charnock's alpha whilst in the first
                       ! he specifies the value 0.032.

  ! Standard temperature :

  real, public, parameter :: T0 = 273.15   ! zero degrees Celsius in Kelvin 

end  module PhysicalConstants_ml
