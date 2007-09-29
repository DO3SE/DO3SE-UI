module Run

    public :: init, Do_Calcs_Python, Do_Calcs

contains

    subroutine init()
        use Soil
        use Variables
        use Params_Site, only: Derive_Windspeed_d_zo, Copy_Windspeed_h_d_zo, &
                Derive_O3_d_zo, Copy_O3_h_d_zo
        use Params_Veg, only: Derive_d_zo
        call Soil_initialize()
        AEt = 0
        PEt = 0
        Ei = 0
        AFstY = 0
        AOT40 = 0
        
        call Derive_d_zo()
        !call Derive_Windspeed_d_zo()
        call Copy_Windspeed_h_d_zo()
        !call Derive_O3_d_zo()
        call Copy_O3_h_d_zo()
    end subroutine init
    
    !==========================================================================
    ! Run the full set of calculations
    !
    ! This subroutine's arguments are subroutines for the following 
    ! calculations that have interchangeable methods:
    !
    ! Derive_Inputs
    !       This should usually be a wrapper function which calls the 
    !       necessary derivation subroutines depending on the data supplied
    !
    ! Calc_SAI
    !       Method for calculating SAI (simple or crops)
    !
    ! Calc_Ra
    !       Method for calculating Ra (simple or including heat flux data)
    !
    ! Calc_PEt
    ! Calc_AEt
    !       Methods for calculating potential and actual evapotranspiration
    !
    ! Calc_Rn
    !       Method for calculating net radiation (copy or calculate)
    !
    !==========================================================================
    subroutine Do_Calcs(Derive_Inputs, Calc_SAI, Calc_Ra, Calc_PEt, Calc_AEt, &
                        Calc_Rn)
        use Phenology, only: Calc_LAI, Calc_fphen
        use Irradiance, only: Calc_sinB, Calc_Flight
        use Environmental, only: Calc_ftemp, Calc_fVPD
        use R, only: Calc_Rb, Calc_Rgs, Calc_Rinc, Calc_Rsto, Calc_Rsur
        use Soil, only: Calc_precip, Calc_SWP, Calc_fSWP
        use Evapotranspiration, only: Calc_Ei
        use O3, only: Calc_O3_Concentration, Calc_Ftot, Calc_Fst, Calc_AFstY, Calc_AOT40
        use Inputs, only: dd
        use Variables, only: dd_prev

        interface
            subroutine Derive_Inputs()
            end subroutine Derive_Inputs
            subroutine Calc_SAI()
            end subroutine Calc_SAI
            subroutine Calc_Ra()
            end subroutine Calc_Ra
            subroutine Calc_PEt()
            end subroutine Calc_PEt
            subroutine Calc_AEt()
            end subroutine Calc_AEt
            subroutine Calc_Rn()
            end subroutine Calc_Rn
        end interface

        call Derive_Inputs()    !***

        call Calc_LAI()
        call Calc_SAI()         !***
        call Calc_fphen()

        call Calc_sinB()
        call Calc_Flight()
        call Calc_Rn()          !***

        call Calc_ftemp()
        call Calc_fVPD()
    
        call Calc_Ra()          !***
        call Calc_Rb()
        call Calc_Rgs()
        call Calc_Rinc()
        call Calc_Rsto()
        call Calc_Rsur()

        call Calc_precip()

        call Calc_PEt()         !***
        call Calc_AEt()         !***
        call Calc_Ei()

        call Calc_SWP()
        call Calc_fSWP()

        call Calc_O3_Concentration()
        call Calc_Ftot()
        call Calc_Fst()
        call Calc_AFstY()
        call Calc_AOT40()

        dd_prev = dd
    end subroutine Do_Calcs

end module Run
