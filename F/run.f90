module Run

    public :: Init, Do_Calcs_Python, Do_Calcs

contains

    subroutine Init(copy_u, copy_o3)
        use Soil
        use Variables
        use Params_Site, only: Derive_Windspeed_d_zo, Copy_Windspeed_h_d_zo, &
                Derive_O3_d_zo, Copy_O3_h_d_zo
        use Params_Veg, only: Derive_d_zo

        integer,intent(in) :: copy_u, copy_o3

        call Soil_initialize()
        
        AEt = 0
        PEt = 0
        Ei = 0
        AFst0 = 0
        AFstY = 0
        AOT0 = 0
        AOT40 = 0
        
        call Derive_d_zo()

        if (copy_u == 1) then
            call Copy_Windspeed_h_d_zo()
        else
            call Derive_Windspeed_d_zo()
        endif

        if (copy_o3 == 1) then
            call Copy_O3_h_d_zo()
        else
            call Derive_O3_d_zo()
        endif
    end subroutine Init
    
    !==========================================================================
    ! Run the full set of calculations
    !
    ! This subroutine's arguments are subroutines for the following 
    ! calculations that have interchangeable methods:
    !
    ! Calc_SAI
    !       Method for calculating SAI (simple or crops)
    !
    ! Calc_leaf_fphen
    !       Method for calculating leaf_fphen (copy fphen, or use special calc)
    !
    ! Calc_Ra
    !       Method for calculating Ra (simple or including heat flux data)
    !
    ! Calc_Rn
    !       Method for calculating net radiation (copy or calculate)
    !
    ! Calc_fO3
    !       Method for calculating fO3 (ignore, wheat or potato)
    !
    !==========================================================================
    subroutine Do_Calcs(Calc_SAI, Calc_leaf_fphen, Calc_Ra, Calc_Rn, Calc_fO3)
        use Phenology, only: Calc_LAI, Calc_fphen
        use Irradiance, only: Calc_sinB, Calc_Flight
        use Environmental, only: Calc_ftemp, Calc_fVPD
        use R, only: Calc_Rb, Calc_Rgs, Calc_Rinc, Calc_Rsto, Calc_Rsur
        use Soil, only: Calc_precip, Calc_SWP
        use Evapotranspiration, only: Calc_Penman_Monteith
        use O3, only: Calc_O3_Concentration, Calc_Ftot, Calc_Fst, Calc_AFstY, Calc_AOT40
        use Inputs, only: dd
        use Variables, only: dd_prev

        interface
            subroutine Calc_SAI()
            end subroutine Calc_SAI
            subroutine Calc_leaf_fphen()
            end subroutine Calc_leaf_fphen
            subroutine Calc_Ra()
            end subroutine Calc_Ra
            subroutine Calc_Rn()
            end subroutine Calc_Rn
            subroutine Calc_fO3()
            end subroutine Calc_fO3
        end interface

        call Calc_LAI()
        call Calc_SAI()         !***
        call Calc_fphen()
        call Calc_leaf_fphen()

        call Calc_sinB()
        call Calc_Flight()
        call Calc_Rn()          !***

        call Calc_ftemp()
        call Calc_fVPD()

        call Calc_fO3()
    
        call Calc_Ra()          !***
        call Calc_Rb()
        call Calc_Rgs()
        call Calc_Rinc()
        call Calc_Rsto()
        call Calc_Rsur()

        call Calc_precip()

        call Calc_Penman_Monteith()

        call Calc_SWP()

        call Calc_O3_Concentration()
        call Calc_Ftot()
        call Calc_Fst()
        call Calc_AFstY()
        call Calc_AOT40()

        dd_prev = dd
    end subroutine Do_Calcs

end module Run
