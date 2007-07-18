module Functions_ml

!================== Now under CVS control =================
! $Author: mifads $
! $Id: Functions_ml.f90,v 1.2 2002/09/12 14:51:07 mifads Exp $
! $Name:  $
! =========================================================

implicit none

public :: Polygon
public :: find_index

contains
!=======================================================================
function Polygon(jdayin,Ymin,Ystart,Ymax,Sday,LenS,Eday,LenE) &
result (Poly)
!=======================================================================

!     Calculates the value of a parameter Y with a polygon
!     distribution - currently LAI and g_pot

!            _____________       <- Ymax
!           /             \
!          /               \
!         /                 \
!        /                   \
!       |                     |  <- Ystart
!       |                     |
!       |                     |
!  ----------------------------- <- Ymin
!       S  S1            E1   E
!
    

!   Inputs
    integer, intent(in) :: jdayin      !day of year
    real, intent(in) ::    Ymin        !minimum value of Y
    real, intent(in) ::    Ystart      !value Y at start of growing season
    real, intent(in) ::    Ymax        !maximum value of Y
    integer, intent(in) ::    Sday        !start day (e.g. of growing season)
    integer, intent(in) ::    LenS        !length of Start period (S..S1 above)
    integer, intent(in) ::    Eday        !end day (e.g. of growing season)
    integer, intent(in) ::    LenE        !length of end period (E..E1 above)

!  Output:
    real ::   Poly  ! value at day jday

! Local
    integer :: jday  ! day of year, after any co-ordinate change
    integer ::    S   !  start day
    integer ::    E   !  end day
    

    jday = jdayin
    E = Eday
    S = Sday

  ! Here we removed a lot of code associated with the leaf-age
  ! version of g_pot. 
       
    if ( jday  <  S .or. jday >  E ) then
       Poly = Ymin
       return
    end if

  ! Here's the real functions....

    if (jday <=  S+LenS  .and. LenS > 0 ) then

        Poly = (Ymax-Ystart) * (jday-S)/LenS  + Ystart 

    else if ( jday >=  E-LenE .and. LenE > 0.0 ) then

        Poly = (Ymax-Ystart) * (E-jday)/LenE + Ystart

    else

        Poly =Ymax
    end if
    

 end function Polygon
!=======================================================================

 function find_index(wanted, list)  result(Index)
    character(len=*), intent(in) :: wanted
    character(len=*), dimension(:), intent(in) :: list
!  Output:
    integer ::   Index       ! 

    integer :: n_match ! Count for safety
    integer :: n

    n_match  = 0
    Index = -1

    do n = 1, size(list)

         if ( wanted == list(n)  ) then
            Index = n
            n_match = n_match + 1
         end if
    end do

    if ( n_match /= 1 ) Index = -99   ! ERROR check: none or too many !

  end function find_index

end module Functions_ml
!=======================================================================
