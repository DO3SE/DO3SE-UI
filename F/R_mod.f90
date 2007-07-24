        module R_mod

            real, public, save  :: Rext
            real, public, save  :: Ra
            real, public, save  :: Rb
            real, public, save  :: Rsur
            real, public, save  :: Rinc
            real, public, save  :: Rext
            real, public, save  :: Rsoil
            real, public, save  :: Rsto

            public :: Calc_Rext, Calc_Rsoil

        contains

        !***********************************************************************
        ! R calculations that do nothing more than copy from parameters
        ! made available to the model
        !***********************************************************************
        subroutine Calc_Rext()
            use Params_Veg_mod, only: Rext_param => Rext
            Rext = Rext_param
        end subroutine Calc_Rext

        subroutine Calc_Rsoil()
            use Params_Site_mod, only: Rsoil_param => Rsoil
            Rsoil = Rsoil_param
        end subroutine Calc_Rsoil

        subroutine Calc_Ra()

        end subroutine Calc_Ra

        end module R_mod
