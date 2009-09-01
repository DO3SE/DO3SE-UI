module DOSE

    public :: Init, ReadData, Derive, Calculate, WriteData, Deinit

    integer,private :: inunit = 8
    integer,private :: outunit = 9
    
contains

    !==========================================================================
    ! Initialise the model, opening the input and output files, and running the
    ! pre-run initialisation to reset the model.
    !==========================================================================
    subroutine Init(infile, outfile)
        use Run, only: Run_Init => Init
    
        character(len=*),intent(in) :: infile, outfile

        ! Open the input file
        open(unit=inunit, file=infile, status="old", action="read", &
                position="rewind")
        
        ! Open the output file
        open(unit=outunit, file=outfile, status="replace", action="write", &
                position="rewind")

        ! Initialize the model.
        !
        ! The two parameters are whether or not the vegetation over which the 
        ! windspeed and O3 (respectively) are measured is the same as the flux 
        ! canopy.  (0 = false, 1 = true)
        call Run_Init(1, 1)

    end subroutine Init

    !==========================================================================
    ! Read data into input variables
    !==========================================================================
    subroutine ReadData(ios)
        use Inputs

        integer,intent(out) :: ios

        read(unit=inunit, fmt=*,  iostat=ios) mm, mdd, dd, hr, Ts_C, VPD, &
                uh_zR, precip, P, O3_ppb_zR, Hd, R, PAR
    end subroutine ReadData


    !==========================================================================
    ! Derive inputs not supplied
    !
    ! NOTE: Rn (net radiation) is handled as a calculation, not as a derivation
    !==========================================================================
    subroutine Derive()
        use Inputs, only: Derive_ustar_uh, Derive_R, Derive_PAR

        call Derive_ustar_uh()
        call Derive_R()
        call Derive_PAR()
    end subroutine Derive

    !==========================================================================
    ! Run calculations
    !==========================================================================
    subroutine Calculate()
        use Run, only: Do_Calcs
        
        use Phenology, only: Calc_SAI_Simple, Calc_SAI_Crops
        use Irradiance, only: Calc_Rn, Copy_Rn
        use R, only: Calc_Ra_Simple, Calc_Ra_With_Heat_Flux

        ! Run the calculations, specifying which interchangeable calculations
        ! to use (for: SAI, Ra, PEt, AEt, Rn)
        call Do_Calcs(Calc_SAI_Simple, &
                      Calc_Ra_Simple, &
                      !Calc_Ra_With_Heat_Flux, &
                      Calc_Rn)
    end subroutine Calculate

    !==========================================================================
    ! Write data to file
    !==========================================================================
    subroutine WriteData()
        use Variables

        write(unit=outunit, fmt=*) &
        !rn, &
        !ra, &
        !rb, &
        !rsur, &
        !rinc, &
        !rsto, &
        !gsto, &
        !rgs, &
        !vd, & 
        !o3_ppb, &
        !o3_nmol_m3, &
        !fst, &
        !afsty, &
        !ftot, &
        !ot40, &
        !aot40, &
        !aet, &
        !swp, &
        !per_vol, &
        !smd, &
        " "
    end subroutine WriteData

    !==========================================================================
    ! Cleanup after the run, closing files
    !==========================================================================
    subroutine Deinit()
        close(unit=inunit)
        close(unit=outunit)
    end subroutine Deinit

end module DOSE

program Run_DOSE
    use DOSE

    integer :: ios

    call Init("input_newstyle.csv", "output.csv")

    read_loop: do
        call ReadData(ios)

        if ( ios /= 0 ) then
            exit read_loop
        end if

        call Derive()
        call Calculate()
        call WriteData()
    end do read_loop

    call Deinit()
end program Run_DOSE

