program Test
    
    use Run
    use Inputs, precip_in => precip
    use Variables

    integer :: ios = 0

    call init()

    open (unit=9, file="2003_input.csv", &
       status="old", action="read", position="rewind")

    read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_c, VPD, precip_in, &
                                    uh, O3_ppb_zR, Idrctt, Idfuse, zen

    dd_prev = dd
    read_loop: do
        if ( ios /= 0) then
            exit read_loop
        end if

        call Do_Calcs()

        print *, Ra_O3, Rb, Rsto, LAI, SAI, Fphen, &
                      Ts_c, precip, &
                      SMD, SWP, fswp, Gsto, Rsur, Vd, &
                      Fst, AFstY, & !gO3, &
                      O3_ppb, PEt, AEt, &
		      Rsto_PEt, Ei, ustar, Sn, &
                      Ftot, Ra, Per_vol

        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_c, VPD, precip_in, &
                                    uh, O3_ppb_zR, Idrctt, Idfuse, zen
    end do read_loop

end program Test

