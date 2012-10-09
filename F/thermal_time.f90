module thermal_time

    use do3se_thermal_time, only: ThermalTimeModelType

    public :: init_thermal_time
    public :: accumulate_tmean
    public :: accumulate_ttime

    type(ThermalTimeModelType), private, save :: ttime_model
    real, private, save :: tsum

contains

    subroutine init_thermal_time()
        use do3se_thermal_time
        use parameters, only: ttime_sowing, ttime_emergence
        use variables, only: ttime

        ttime_model = do3se_create_thermal_time_model(ttime_sowing, ttime_emergence)
        ttime = 0.0
        tsum = 0.0
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
    end subroutine accumulate_ttime

end module thermal_time
