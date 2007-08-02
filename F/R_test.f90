program test_R
    use Inputs_mod
    use R_mod

    integer :: ios = 0

    open (unit=9, file="2003_input.csv", &
       status="old", action="read", position="rewind")

    read_loop: do
        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_c, VPD, precip, &
                                        uh, O3_ppb_zR, Idrctt, Idfuse, zen
        
        if ( ios /= 0) then
            exit read_loop
        end if

        call Input_sanitize()

        call Calc_ustar()
        call Calc_Ra()
        call Calc_Rb()

        print *, ustar, Ra, Rb
    end do read_loop

end program test_R
