module Run

    public :: init, Do_Calcs

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

    subroutine Do_Calcs()
        use Inputs, only: dd, Derive_R, Derive_PAR, Derive_ustar_uh
        use Variables, only: dd_prev
        use Phenology, Calc_SAI => Calc_SAI_Simple
        use R
        use Irradiance
        use Environmental
        use Soil
        use Evapotranspiration
        use O3
    
        ! Run input derivations
        !call Derive_R()
        !call Derive_PAR()
        call Derive_ustar_uh()

        call Calc_LAI()     !
        call Calc_SAI()     !
        call Calc_fphen()   !

        call Calc_sinB()
        call Calc_Flight()
        call Calc_Rn()

        call Calc_ftemp()   !
        call Calc_fVPD()    !
    
        call Calc_Ra()      !
        call Calc_Rb()      !
        call Calc_Rgs()     !
        call Calc_Rinc()    !
        call Calc_Rsto()    !
        call Calc_Rsur()    !

        call Calc_precip()  !

        call Calc_PEt()     !
        call Calc_AEt()     !
        call Calc_Ei()      !

        call Calc_SWP()     !
        call Calc_fSWP()    !

        !call Calc_Vd()      !
        call Calc_O3_Concentration()    !
        call Calc_Ftot()    !
        call Calc_Fst()     !
        call Calc_AFstY()   !
        call Calc_AOT40()

        dd_prev = dd

    end subroutine Do_Calcs
end module Run
