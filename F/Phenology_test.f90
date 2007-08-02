program test_Phenology
    use Phenology_mod
    use Inputs_mod

    integer :: ios = 0
    integer :: line = 0

    open (unit=9, file="2003_input.csv", &
       status="old", action="read", position="rewind")

    read_loop: do
        read (unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr
        
        line = line + 1

        if ( ios /= 0) then
            exit read_loop
        end if

        call Calc_LAI()
        call Calc_SAI_Simple()
        call Calc_fphen()

        print *, LAI, SAI, fphen
    end do read_loop

end program test_Phenology
