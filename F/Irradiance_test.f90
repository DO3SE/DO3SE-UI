program test_Irradiance
    use Phenology_mod
    use Irradiance_mod
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

        call Calc_LAI()
        call Calc_SAI_Simple()
        call Calc_fphen()
        call Calc_Flight()


        print *, PARshade, PARsun, flight, leaf_flight
    end do read_loop

end program test_Irradiance
