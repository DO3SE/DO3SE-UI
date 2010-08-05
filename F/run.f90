module Run

    public :: Run_With_Callbacks
    public :: Run_With_Files

    public :: Initialise
    public :: Hourly
    public :: Daily
    public :: Calculate_Row
    public :: Open_Files
    public :: Close_Files
    public :: Read_Row_From_File
    public :: Write_Row_To_File

    !integer, private :: dd_prev
    integer, private :: inunit = 8
    integer, private :: outunit = 9

contains

    subroutine Initialise()
        use Switchboard
        use Variables
        use SoilWater
        use params_veg, only: Derive_d_zo
        use params_site, only: Derive_Windspeed_d_zo, Derive_O3_d_zo
        use Inputs, only: Init_Inputs

        dd_prev = -1
        
        AFst0 = 0
        AFstY = 0
        AOT0 = 0
        AOT40 = 0

        ! Put calls to initialisation functions here
        call Derive_d_zo()
        call Derive_Windspeed_d_zo()
        call Derive_O3_d_zo()
        call Init_Inputs()
        call Init_SoilWater()
    end subroutine Initialise

    subroutine Hourly()
        use Environmental, only: Calc_ftemp, Calc_fVPD, Calc_Flight
        use R, only: Calc_Rb, Calc_Rgs, Calc_Rinc, Calc_Rsto, Calc_Rsur
        use SoilWater
        use O3, only: Calc_O3_Concentration, Calc_Ftot, Calc_Fst, Calc_AFstY, Calc_AOT40
        use Inputs, only: dd, Calc_ustar_uh, Accumulate_precip, Calc_sinB
        use Variables, only: dd_prev

        use Switchboard


        ! Derivation of inputs not supplied
        call Accumulate_precip()
        call Calc_ustar_uh()
        call SB_Calc_R_PAR()
        call Calc_sinB()
        call SB_Calc_Rn()

        call Calc_Flight()

        call Calc_ftemp()
        call Calc_fVPD()

        call SB_Calc_fO3()
        call SB_Calc_fXWP()
    
        call SB_Calc_Ra()
        call Calc_Rb()
        call Calc_Rgs()
        call Calc_Rinc()
        call Calc_Rsto()
        call Calc_Rsur()

        call Calc_Penman_Monteith()

        call SB_Calc_LWP()  ! This *must* happen after calculating SWP - SWP is 
                            ! calculated as the day rolls over, and LWP should 
                            ! use the previous day's SWP
        call Calc_fLWP()

        call Calc_O3_Concentration()
        call Calc_Ftot()
        call Calc_Fst()
        call Calc_AFstY()
        call Calc_AOT40()
    end subroutine Hourly

    subroutine Daily()
        use SoilWater
        use Switchboard
        use Phenology, only: Calc_LAI, Calc_fphen
        use Inputs, only: Calc_precip_acc

        call Calc_LAI()
        call SB_Calc_SAI()
        call Calc_fphen()
        call SB_Calc_leaf_fphen()

        call Calc_precip_acc()
        call Calc_Penman_Monteith_daily()
        call Calc_SWP()
        call SB_Calc_fSWP()
        call Calc_SWP_meas()
        call Calc_fPAW()
    end subroutine Daily

    subroutine Calculate_Row()
        use Inputs, only: dd
        use Variables, only: dd_prev

        ! At the start of a new day, do daily actions on previous day's data
        if (dd_prev /= dd) then
            call Daily()
        end if

        ! Run hourly calculations
        call Hourly()

        dd_prev = dd
    end subroutine Calculate_Row

    subroutine Open_Files(infile, outfile)
        character(len=*), intent(in) :: infile, outfile

        open(unit=inunit, file=infile, status="old", &
             action="read", position="rewind")
        open(unit=outunit, file=outfile, status="replace", &
             action="write", position="rewind")

        call Initialise()
    end subroutine Open_Files

    subroutine Close_Files()
        close(unit=inunit)
        close(unit=outunit)
    end subroutine Close_Files

    subroutine Read_Row_From_File(done)
        use Inputs

        logical, intent(out) :: done
        integer :: ios

        read(unit=inunit, fmt=*, iostat=ios) &
            mm, mdd, dd, hr, Ts_C, VPD, uh_zR, precip, P, O3_ppb_zR, Hd, R, PAR

        if (ios /= 0) then
            done = .TRUE.
        else
            done = .FALSE.
        end if
    end subroutine Read_Row_From_File

    subroutine Write_Row_To_File()
        use Inputs
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
    end subroutine Write_Row_To_File

    subroutine Run_With_Callbacks(Read_Row, Write_Row)
        logical :: done = .FALSE.

        interface
            subroutine Read_Row(done)
                logical, intent(out) :: done
            end subroutine Read_Row
            subroutine Write_Row()
            end subroutine Write_Row
        end interface

        call Initialise()

        do
            call Read_Row(done)
            if (done) then
                exit
            end if

            call Calculate_Row()

            call Write_Row()
        end do
    end subroutine Run_With_Callbacks

    subroutine Run_With_Files(infile, outfile)
        character(len=*), intent(in) :: infile, outfile

        call Open_Files(infile, outfile)
        call Run_With_Callbacks(Read_Row_From_File, Write_Row_To_File)
        call Close_Files()
    end subroutine Run_With_Files

end module Run
