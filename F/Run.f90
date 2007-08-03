module Run

    public :: init, Do_Calcs

contains

    subroutine init()
        use Soil_mod
        use Variables_mod
        call Soil_initialize()
        AEt = 0
        PEt = 0
        Ei = 0
        AFstY = 0
        AOT40 = 0
    end subroutine init

    subroutine Do_Calcs()
        use Inputs_mod, only: Input_sanitize, dd
        use Variables_mod, only: dd_prev
        use Phenology_mod, Calc_SAI => Calc_SAI_Simple
        use R_mod
        use Irradiance_mod
        use Environmental_mod
        use Soil_mod
        use Evapotranspiration_mod
        use O3_Flux_mod
        use O3_Effects_mod
        
        call Input_sanitize()

        call Calc_LAI()     !
        call Calc_SAI()     !
        call Calc_fphen()   !

        call Calc_flight()  !
        call Calc_ftemp()   !
        call Calc_fVPD()    !
    
        call Calc_ustar()   !
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

        call Calc_Vd()      !
        call Calc_O3_Concentration()    !
        call Calc_Ftot()    !

        call Calc_Fst()     !
        call Calc_AFstY()   !
        call Calc_AOT40()

        dd_prev = dd

    end subroutine Do_Calcs
end module Run
