        program FooBar
            use A_mod, only: set_foo
            use B_mod, only: get_foo

            integer :: x = 1

            call set_foo(x)
            print *, get_foo()
            x = 2
            call set_foo(x)
            print *, get_foo()
        end program FooBar
