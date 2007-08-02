module Environmental_mod

    real, public, save  :: ftemp
    real, public, save  :: fVPD

    public :: Calc_ftemp, Calc_fVPD

contains

    !***************************************************************************
    ! Calculate ftemp
    !***************************************************************************
    subroutine Calc_ftemp()
        use Inputs_mod, only: Ts_c
        use Params_Veg_mod, only: T_max, T_min, T_opt, fmin

        real :: bt 
        
        bt = (T_max - T_opt) / (T_opt - T_min)
        ftemp = max(((Ts_c-T_min)/(T_opt-T_min))*((T_max-Ts_c)/(T_max-T_opt))**bt, fmin)
    end subroutine Calc_ftemp

    !***************************************************************************
    ! Calculate fVPD (vapour pressure deficit related g)
    !***************************************************************************
    subroutine Calc_fVPD()
        use Inputs_mod, only: VPD
        use Params_Veg_mod, only: fmin, VPD_min, VPD_max

        fVPD = ((1 - fmin)*(VPD_min - VPD)/(VPD_min - VPD_max)) + fmin
        fVPD = max(fVPD, fmin)

        if ( fVPD > 1 ) then
            fVPD = 1
        end if
    end subroutine Calc_fVPD

end module Environmental_mod
