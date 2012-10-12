program Run_DOSE
    use ISO_FORTRAN_ENV
    use Parameters
    use Switchboard
    use Run

    character(len=*), parameter :: usage = "usage: run_do3se config.nml [inputfile [outputfile]]"

    integer :: inunit = INPUT_UNIT
    integer :: outunit = OUTPUT_UNIT
    integer :: configunit

    integer :: errstat
    integer :: arglen
    character(len=1024) :: argbuffer

    ! Get confiuration file
    call get_command_argument(1, argbuffer, arglen, errstat)
    if (arglen == 0 .or. errstat > 0) then
        call die(1, 'No configuration file specified' // new_line(' ') // usage)
    else if (errstat < 0) then
        call die(1, "Configuration file path too long")
    end if

    ! Load configuration
    open(newunit=configunit, file=argbuffer, status="old", action="read", position="rewind")
    call load_parameters(configunit)
    call load_switchboard_settings(configunit)
    close(configunit)

    ! Open input file, if specified
    call GET_COMMAND_ARGUMENT(2, argbuffer, arglen, errstat)
    if (errstat < 0) then
        call die(1, "Input file path too long")
    else if (arglen > 0 .and. errstat == 0) then
        OPEN (newunit=inunit, file=argbuffer, status="old", action="read", position="rewind")
    end if

    ! Open output file, if specified
    call GET_COMMAND_ARGUMENT(3, argbuffer, arglen, errstat)
    if (errstat < 0) then
        call die(1, "Output file path too long")
    else if (arglen > 0 .and. errstat == 0) then
        OPEN (newunit=outunit, file=argbuffer, status="replace", action="write", position="rewind")
    end if

    call Run_With_Units(inunit, outunit)

    if (inunit /= INPUT_UNIT) then
        close(inunit)
    end if
    if (outunit /= OUTPUT_UNIT) then
        close(outunit)
    end if

    call dump_year_stats()

contains

    ! Print a message to stderr and exit with a particular status code.
    ! (exitstatus=0 for success)
    subroutine die(exitstatus, message)
        use ISO_FORTRAN_ENV, only: ERROR_UNIT
        integer, intent(in) :: exitstatus
        character(len=*), intent(in) :: message
        WRITE (ERROR_UNIT, '(a)') message
        call EXIT(exitstatus)
    end subroutine die

    subroutine dump_year_stats()
        use thermal_time
        use variables, only: AFstY

        print *, ttime_season%SGS, ttime_season%double_ridge, &
                 ttime_season%Astart, ttime_season%mid_anthesis, &
                 ttime_season%Aend, AFstY
    end subroutine dump_year_stats

end program Run_DOSE
