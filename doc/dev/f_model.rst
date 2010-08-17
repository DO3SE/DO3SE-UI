:mod:`do3se_fortran` -- The F Model
===================================

.. module:: do3se_fortran

:mod:`do3se_fortran.run` -- Model run framework
-----------------------------------------------

.. module:: do3se_fortran.run

.. function:: initialise

    This subroutine is run before any data is processed.  Its main purpose is to call all the other 
    initialisation subroutines so that everything is ready for running.  If a new module is created 
    and it has, for example, accumulated values, then it should have an initialisation subroutine 
    that sets the starting values of those variables, and that initialisation subroutine should be 
    called from :func:`initialise`.

.. function:: hourly

    This subroutine is run for every row of data.  It consists of calls to subroutines which each 
    perform some calculation.  It is important that these subroutines are ordered such that any 
    calculation that uses the result of another calculation happens after that other calculation.  
    For example, the calculation of @Flight@ depends on the value of @sinB@ for that hour, and 
    therefore :func:`hourly` contains

    .. code-block:: fortran

        subroutine Hourly()
            ! ...
            call Calc_sinB()
            call Flight()
            ! ...
        end subroutine Hourly

.. function:: daily

    This subroutine is run on the first hour of every day of the dataset, before :func:`hourly` is 
    called.  Calculations which happen on a daily basis should be called here.  Anything which has 
    an hourly component and a daily component should be split into two separate subroutines so they 
    can be called from :func:`daily` and :func:`hourly` as appropriate.

    For example, a simple daily accumulated variable may have been calculated like this:

    .. code-block:: fortran

        foo = 0
        foo_dd = 0
        ! ...
        if (dd_prev /= dd) then
            foo = foo_dd
            foo_dd = x
        else
            foo_dd = foo_dd + x
        end if

    After restructuring, the code should have initialisation, hourly and daily components:

    .. code-block:: fortran

        module Example
            real, public :: foo
            real, private :: foo_dd
        contains
            subroutine Init_Example()
                foo = 0
                foo_dd = 0
            end subroutine Init_Example

            subroutine Accumulate_foo()
                foo_dd = foo_dd + x
            end subroutine Accumulate_foo

            subroutine Daily_foo()
                foo = foo_dd
                foo_dd = 0
            end subroutine Daily_foo
        end module Example

    While this is not as short, it does have the advantage of clearly defining the boundary between 
    hourly actions and daily actions.  Since all daily actions happen before all hourly actions, any 
    hourly calculation depending on a daily accumulated variable from the previous day will have use 
    the correct value.


:mod:`do3se_fortran.switchboard` -- Calculation switchboard
-----------------------------------------------------------

.. module:: do3se_fortran.switchboard
    :synopsis: Calculation switchboard

Several parts of the DO3SE model have different calculations for the same thing, and there needs to 
be some way for the GUI to switch between these.  The preferred method would be using module-level 
``interface`` statements, unfortunately none of the available Fortran-to-Python integration tools 
support these.  Instead we use an overly verbose but consistent method; for each switchable 
calculation, there exists several constants in :file:`switchboard.f90`, each numbered differently, 
which represent the available calculations and a single variable which is set to one of these 
constants to select the appropriate calculation.  There is also a subroutine for each switchable 
calculation which executes a ``select case`` statement on its related variable and performs the 
appropriate action depending on the value.
