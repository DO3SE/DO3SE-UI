        module A_mod
            use Variables_mod, only: foo

            public :: set_foo

        contains

            subroutine set_foo(x)
                integer, intent(in) :: x
                foo = x
            end subroutine set_foo
        end module A_mod
