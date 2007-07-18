        program DOSE_file
            use DOSE_module

            integer :: I, ios, max_lines
            type(input_record) :: input
            type(output_record) :: output

            call init()

            max_lines = 400000

            open (unit = 9, file = "2003_input.csv", status = "old", &
                action = "read", position = "rewind")
            open (unit = 8, file = "test_output", status = "replace", &
                action = "write", position = "rewind")

            do I = 1, max_lines
                read (unit = 9, fmt = *, iostat = ios) input

                if (ios /= 0) then
                    print *, "End of file"
                    exit
                end if

                !print *, input
                call run(input, output)
                !print *, output
                write (unit = 8, fmt = *) output

            end do

            close(unit = 9)
            close(unit = 8)
        end program DOSE_file
