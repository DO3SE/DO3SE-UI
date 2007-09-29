program Test
    
    use Run
    use Inputs, GR => R, precip_in => precip, Rn_in => Rn
    use Variables

    use Phenology, only: Calc_SAI_Simple
    use R, only: Calc_Ra_With_Heat_Flux, Calc_Ra_Simple
    use Evapotranspiration, only: Calc_PEt, Calc_AEt
    use Irradiance, only: Calc_Rn

    integer :: ios = 0
    real :: foo_a

    call init()

    open (unit=9, file="input_newstyle.csv", &
       status="old", action="read", position="rewind")

    read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_C, VPD, uh_zR, &
            precip_in, P, O3_ppb_zR, foo_a, Hd, GR, PAR

    dd_prev = dd
    read_loop: do
        if ( ios /= 0) then
            exit read_loop
        end if

        call Do_Calcs(  Derive_ustar_uh, &
                        Calc_SAI_Simple, &
                        Calc_Ra_With_Heat_Flux, &
                        Calc_PEt, &
                        Calc_AEt, &
                        Calc_Rn)

        print *, o3_ppb_zr, o3_ppb

        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_C, VPD, uh_zR, &
                precip_in, P, O3_ppb_zR, foo_a, Hd, GR, PAR
    end do read_loop

end program Test

