module Functions_mod

    public :: Polygon, newPolygon

contains
    
    !*******************************************************************
    !   
    !  y|      ____________
    !   |     /            \
    !  z|    /              \___
    !  x|___/                
    !   |_______________________
    !       a  b          c d
    !
    ! This function finds the value on the y-axis for a given x-axis 
    ! value on a graph that follows the generic 3-level polygon 
    ! shape
    !*******************************************************************
    function Polygon(a, b, c, d, x, y, z, value) result(retval)
        real, intent(in) :: a, b, c, d, x, y, z, value
        real :: retval

        if ( value < a ) then
            retval = x
        else if ( value < b ) then
            retval = x + (((value - a)/(b - a)) * (y - x))
        else if ( value < c ) then
            retval = y
        else if ( value < d ) then
            retval = y - (((value - c)/(d - c)) * (y - z))
        else
            retval = z
        end if
    end function Polygon

    !*******************************************************************
    !   
    !   |  x ____________
    !   |   /            \
    !   |w /              \
    !   |  |               \ y
    !  v|__|               |
    !   |                  |___ z
    !   |______________________
    !      a b          c  d
    !
    ! TODO: Make this work
    !
    ! This function finds the value on the y-axis for a given x-axis 
    ! value on a graph that follows a polygon shape
    !*******************************************************************
    function newPolygon(a, b, c, d, v, w, x, y, z, value) result(retval)
        real, intent(in) :: a, b, c, d, v, w, x, y, z, value
        real :: retval

        print *, v, w, x, y, z

        if ( value < a ) then
            retval = v
        else if ( value < b ) then
            retval = x + (((value - a)/(b - a)) * (x - w))
        else if ( value < c ) then
            retval = x
        else if ( value < d ) then
            retval = y + (((value - c)/(d - c)) * (x - z))
        else
            retval = z
        end if
    end function newPolygon

end module Functions_mod
