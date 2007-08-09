module Inputs_mod

    real, public, save   :: mm, mdd, dd, hr, Ts_c, VPD, precip, uh, O3_ppb_zR, &
                            Idrctt, Idfuse, zen
    
    public :: Input_sanitize

contains
    
    subroutine Input_sanitize()
        ! Prevent windspeed from being 0
        if ( uh <= 0 ) then
            uh = 0.001
        end if
    end subroutine Input_sanitize

end module Inputs_mod
