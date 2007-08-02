module R_mod

    real, public, save  :: Rext
    real, public, save  :: Ra
    real, public, save  :: Rb
    real, public, save  :: Rsur
    real, public, save  :: Rinc
    real, public, save  :: Rsoil
    real, public, save  :: Rsto

    real, public, save  :: ustar
    real, public, save  :: Uzh

    public :: Calc_Rext, Calc_Rsoil, Calc_ustar, Calc_Ra, Calc_Rb

contains

    !***************************************************************************
    ! R calculations that do nothing more than copy from parameters
    ! made available to the model
    !***************************************************************************
    subroutine Calc_Rext()
        use Params_Veg_mod, only: Rext_param => Rext
        Rext = Rext_param
    end subroutine Calc_Rext

    subroutine Calc_Rsoil()
        use Params_Site_mod, only: Rsoil_param => Rsoil
        Rsoil = Rsoil_param
    end subroutine Calc_Rsoil


    !***************************************************************************
    ! Calculate ustar - resistance velocity
    !***************************************************************************
    subroutine Calc_ustar()
        use Constants_mod, only: uzR, d, zo, k
        use Inputs_mod, only: uh

        ustar = (uh * k) / log((uzR - d) / (zo))
    end subroutine Calc_ustar
   

    !***************************************************************************
    ! Calculate Ra, Atmospheric resistance
    !***************************************************************************
    subroutine Calc_Ra()
        use Constants_mod, only: uzR, d, zo, k, h

        if ( uzR < zo + d ) then
            Ra = 1 / (k * ustar) * (log(((zo + d) - d)/(h - d)))
        else
            Ra = 1 / (k * ustar) * (log((uzR - d)/(h - d)))
        end if
    end subroutine Calc_Ra

    !***************************************************************************
    ! Calculate Rb, quasi-laminar boundary layer resistance, s/m
    !***************************************************************************
    subroutine Calc_Rb()
        use Constants_mod, only: k, v, DO3, Pr

        Rb = (2/(k*ustar)) * ((v/DO3/Pr)**(2/3))
    end subroutine Calc_Rb

end module R_mod
