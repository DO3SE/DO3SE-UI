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
            function OddPolygon(a, b, c, d, x, y, z, value) result(retval)
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

            !*******************************************************************
            !   
            !          |
            !    Ymax  |        ________________
            !          |       /                \
            !          |      /                  \
            !    Ystart|     /                    \
            !          |     |                    |
            !          |     |                    |
            !    Ymin  +---------------------------------
            !                S  S1            E1  E
            !
            !                S1 = S + dtS
            !                E1 = E - dtE
            !
            ! This function finds the value on the y-axis for a given x-axis 
            ! value on a graph that follows the above shape
            !*******************************************************************
            function Polygon(value, Ymin, Ymax, Ystart, 
                                S, dtS, E, dtE) result(retval)
                real :: value, Ymin, Ymax, Ystart, S, dtS, E, dtE
                
                if ( value < S .or. value > E )
                    retval = Ymin
                elseif ( value < (S + dtS) )
                    retval = ((value - S) / dtS) * (Ymax - Ystart) + Ystart
                elseif ( value > (E - dtE) )
                    retval = Ystart - ((E - value) / dtE) * (Ymax - Ystart)
                else
                    retval = Ymax
                endif
        end module Functions_mod
