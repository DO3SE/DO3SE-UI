module Environmental

    public :: Calc_ftemp, Calc_fVPD, Calc_Flight

    private

contains


    !***************************************************************************
    ! Calculate ftemp
    !***************************************************************************
    subroutine Calc_ftemp()
        use Variables, only: ftemp
        use Inputs, only: Ts_c
        use Parameters, only: T_max, T_min, T_opt, fmin

        use do3se_env, only: do3se_f_temp

        ftemp = do3se_f_temp(Ts_C, T_min, T_opt, T_max, fmin)
    end subroutine Calc_ftemp


    !***************************************************************************
    ! Calculate fVPD (vapour pressure deficit related g)
    !***************************************************************************
    subroutine Calc_fVPD()
        use Variables, only: fVPD
        use Inputs, only: VPD
        use Parameters, only: fmin, VPD_min, VPD_max

        use do3se_env, only: do3se_f_VPD

        fVPD = do3se_f_VPD(VPD, VPD_min, VPD_max, fmin)
    end subroutine Calc_fVPD


    !==========================================================================
    ! Calculate Flight and flight
    !==========================================================================
    subroutine Calc_Flight()
        use Parameters, only: f_lightfac, cosA
        use Inputs, only: P, PAR, sinB
        use Variables, only: LAI, Flight, leaf_flight

        use do3se_met, only: do3se_PAR_components
        use do3se_env, only: do3se_f_light
        use do3se_utils, only: do3se_sunlit_LAI

        real :: Idrctt, Idfuse, sunLAI

        call do3se_PAR_components(P, PAR/4.57, sinB, Idrctt, Idfuse)
        sunLAI = do3se_sunlit_LAI(LAI, sinB)
        call do3se_f_light(Idrctt, Idfuse, sinB, LAI, sunLAI/LAI, f_lightfac, cosA, &
                           Flight, leaf_flight)
    end subroutine Calc_Flight

end module Environmental
