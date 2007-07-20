        module B_mod
            use Variables_mod, only: foo

            public :: get_foo

        contains
            
            function get_foo() result(x)
                integer :: x
                x = foo
            end function get_foo
        end module B_mod
