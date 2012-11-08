!
! Useful utilities for handling IO within the DO3SE modle
!
module DO3SE_IO

    public :: err
    public :: die

contains

    ! Output *message* to stderr
    subroutine err(message)
        use ISO_FORTRAN_ENV, only: ERROR_UNIT

        character(len=*), intent(in) :: message

        write (ERROR_UNIT, *) message
    end subroutine err

    ! Write an error message and exit with a non-zero status (1 by default)
    subroutine die(message, exitstatus)
        character(len=*), intent(in) :: message
        integer, intent(in), optional :: exitstatus
        integer, parameter :: DEFAULT_EXIT_STATUS = 1

        call err(message)

        if (present(exitstatus)) then
            call exit(exitstatus)
        else
            call exit(DEFAULT_EXIT_STATUS)
        end if
    end subroutine die

end module DO3SE_IO
