module Main

    ! Input row format
    type InputRow
        integer :: year
        integer :: month
        integer :: dayofmonth
        integer :: dayofyear
        integer :: hour         ! Hour of day, 0-23
        real    :: Tair         ! Air temperature, degrees C
        real    :: Tleaf        ! Leaf temperature, degrees C
        real    :: VPD          ! Vapour pressure deficit, kPa
        real    :: u_zu         ! Windspeed at measurement height zu, m s-1
        real    :: precip       ! Precipitation, mm
        real    :: P            ! Atmospheric presure, kPa
        real    :: O3_ppb_zO3   ! O3 concentration at measurement height zO3, ppb
        real    :: CO2          ! Ambient CO2 concentration, ppm
        real    :: Hd           ! Sensible heat flux, W m-2
        real    :: R            ! Global radiation, W m-2
        real    :: PAR          ! Photosynthetically active radiation, W m-2
        real    :: Rn_MJ        ! Net radiation, MJ m-2
        real    :: leaf_fphen   ! Leaf Fphen input, fraction
    end type InputRow


    ! Derived or calculated input data
    type InputExtra
!        real    :: PPFD         ! Photosynthetic photon flux density, umol m-2 s-1
        real    :: Rn_W         ! Net radiation, W m-2
        logical :: is_beginning_of_day
    end type InputExtra


    ! Input data options, controlling available derivations etc.
    type InputOptions
        logical :: calculate_Tleaf
        logical :: calculate_PAR_from_R
        logical :: calculate_R_from_PAR
        logical :: use_constant_CO2
        real    :: constant_CO2
        logical :: calculate_Rn
        logical :: use_input_leaf_fphen
    end type InputOptions

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

end module Main


program DO3SE

    use ISO_FORTRAN_ENV, only: INPUT_UNIT, OUTPUT_UNIT, IOSTAT_EOR, IOSTAT_END
    use Main

    character(len=*), parameter :: usage = "usage: do3se config.nml [inputfile [outputfile]]"

    integer :: inunit = INPUT_UNIT
    integer :: outunit = OUTPUT_UNIT
    integer :: configunit
    integer :: errstat
    character(len=256) :: argbuffer
    integer :: arglen

    type(InputOptions) :: input
    namelist /do3se_config/ input

    character(len=512) :: linebuffer
    type(InputRow) :: inrow

    ! Load configuration file
    call GET_COMMAND_ARGUMENT(1, argbuffer, arglen, errstat)
    if (arglen == 0 .or. errstat > 0) then
        call die(1, 'No configuration file specified' // NEW_LINE(' ') // usage)
    else if (errstat < 0) then
        call die(1, "Configuration file path too long")
    end if
    OPEN (newunit=configunit, file=argbuffer, status="old", action="read", position="rewind")
    READ (unit=configunit, nml=do3se_config, iostat=errstat)
    if (errstat /= 0) then
        call die(1, "Error reading configuration file")
    end if
    CLOSE (configunit)

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


    do
        ! Force line-at-a-time reads
        READ (unit=inunit, fmt='(a)', iostat=errstat) linebuffer
        if (errstat == IOSTAT_END) then
            call die(0, "Reached end of input file")
        end if

        ! Read row data from the input
        READ (unit=linebuffer, fmt=*, iostat=errstat) inrow
        if (errstat == IOSTAT_END) then
            call die(1, "Incomplete input row")
        end if

        WRITE (unit=outunit, fmt=*) inrow
    end do


    ! Close input and output files if they were opened
    if (inunit /= INPUT_UNIT) then
        CLOSE (inunit)
    end if
    if (outunit /= OUTPUT_UNIT) then
        CLOSE (outunit)
    end if

end program DO3SE
