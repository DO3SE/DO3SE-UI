program test_Irradiance
    use Soil_mod, precip_out => precip
    use Variables_mod, only: dd_prev
    use Inputs_mod

    integer :: ios = 0

    open (unit=9, file="2003_input.csv", &
       status="old", action="read", position="rewind")

    read_loop: do
        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_c, VPD, precip, &
                                        uh, O3_ppb_zR, Idrctt, Idfuse, zen
        
        if ( ios /= 0) then
            exit read_loop
        end if

        call Calc_precip()

        print *, precip_out, SWP
        dd_prev = dd
    end do read_loop

end program test_Irradiance
