module thermal_time

    use do3se_thermal_time, only: ThermalTimeModelType, ThermalTimeSeasonType

    public :: init_thermal_time
    public :: accumulate_tmean
    public :: accumulate_ttime
    public :: calc_ttime_phenology

    type(ThermalTimeModelType), public, save :: ttime_model
    type(ThermalTimeSeasonType), public, save :: ttime_season
    real, private, save :: tsum

contains

    subroutine init_thermal_time()
        use do3se_thermal_time
        use parameters, only: ttime_sowing, ttime_emergence
        use variables, only: ttime

        type(ThermalTimeSeasonType) :: new_season

        ttime_model = do3se_create_thermal_time_model(ttime_sowing, ttime_emergence)
        ttime = 0.0
        tsum = 0.0
        ttime_season = new_season
    end subroutine init_thermal_time

    subroutine accumulate_tmean()
        use inputs, only: ts_c
        tsum = tsum + ts_c
    end subroutine accumulate_tmean

    subroutine accumulate_ttime()
        use do3se_thermal_time
        use inputs, only: dd, ts_c
        use variables, only: tmean, ttime

        tmean = tsum / 24.0
        tsum = 0.0
        call do3se_accumulate_thermal_time(ttime_model, dd, tmean, ttime)
        call do3se_update_thermal_season(ttime_model, dd, ttime, ttime_season)
    end subroutine accumulate_ttime

    subroutine calc_ttime_phenology()
        use do3se_thermal_time
        use variables, only: ttime, LAI, SAI, fphen, leaf_fphen

        LAI = thermal_time_wheat_LAI(ttime_model, ttime)
        SAI = thermal_time_wheat_SAI(ttime_model, ttime, LAI)
        fphen = thermal_time_canopy_f_phen(ttime_model, ttime)
        leaf_fphen = thermal_time_leaf_f_phen(ttime_model, ttime)
    end subroutine calc_ttime_phenology

end module thermal_time
