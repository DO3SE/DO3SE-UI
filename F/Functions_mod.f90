        module Functions_mod

            public :: Polygon

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

                if ( value <= a )
                    retval = x
                elseif ( value >= d )
                    retval = z
                elseif ( value > b .and. value < c )
                    retval = y
                elseif ( value < b ) ! implicitly > a
                    retval = x + (((value - a)/(b - a)) * (y - x))
                elseif ( value > c ) ! implicitly < d
                    retval = y - (((value - c)/(d - c)) * (y - z))
                endif
            end function Polygon

            function SymPolygon(Ymin, Ymax, Ystart, 

        end module Functions_mod
