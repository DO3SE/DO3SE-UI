:mod:`do3se_fortran` -- The F Model
===================================

.. module:: do3se_fortran

:mod:`do3se_fortran.run` -- Model run framework
-----------------------------------------------

.. module:: do3se_fortran.run

.. function:: daily()

    The :func:`daily` subroutine is run before anything else for every row where the day is not the 
    same as the previous row's day.

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
