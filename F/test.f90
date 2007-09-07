program Test
    
    use Run
    use Inputs, precip_in => precip, Rn_in => Rn
    use Variables

    integer :: ios = 0
    real :: foo_a

    call init()

    open (unit=9, file="input_newstyle.csv", &
       status="old", action="read", position="rewind")

    read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_C, VPD, u_zR, &
            precip_in, P, O3_ppb_zR, foo_a, Hd, R, PAR

    dd_prev = dd
    read_loop: do
        if ( ios /= 0) then
            exit read_loop
        end if

        call Do_Calcs()

        !print *, Rn

        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_C, VPD, u_zR, &
                precip_in, P, O3_ppb_zR, foo_a, Hd, R, PAR
    end do read_loop

end program Test

