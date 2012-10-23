module DO3SE_thermal_time

    type ThermalTimeModelType
        real :: start_day           ! Day to start thermal time accumulation
        real :: SGS                 ! Start of growing season (degree days)
        real :: mid_anthesis        ! Mid-anthesis phase (degree days)
        real :: EGS                 ! End of growing season (degree days)
        real :: double_ridge        ! Double ridge phase (degree days)
        real :: Astart              ! Start of accumulation period (degree days)
        real :: Aend                ! End of accumulation period (degree days)
        ! Canopy f_phen polygonal chain parameters
        real :: canopy_f_phen_points(2, 4)
        real :: canopy_f_phen_before
        real :: canopy_f_phen_after
        ! Leaf f_phen polygonal chain parameters
        real :: leaf_f_phen_points(2, 4)
        real :: leaf_f_phen_before
        real :: leaf_f_phen_after
        ! LAI polygonal chain parameters
        real :: LAI_points(2, 4)
        real :: LAI_before
        real :: LAI_after
    end type ThermalTimeModelType

    public :: do3se_create_thermal_time_model

contains

    ! =========================================================================
    ! Populate a ThermalTimeModelType with a *start_day* (before which thermal
    ! time is not accumulated) and parameters derived from *emergence* (the
    ! thermal time that accumulates before the start of the growing season).
    !
    ! For winter wheat, which is assumed to have been sown and emerged before
    ! the winter, these values will be 0 and 0.0.  For spring wheat with a
    ! sowing date of d, they will be d and 70.0.
    ! =========================================================================
    pure function do3se_create_thermal_time_model(start_day, emergence) result (model)
        ! Inputs
        integer, intent(in) :: start_day
        real,    intent(in) :: emergence
        ! Output
        type(ThermalTimeModelType) :: model
        ! Constants
        real, parameter :: SGS_TO_MID = 1075.0
        real, parameter :: MID_TO_EGS = 700.0
        real, parameter :: EMERGENCE_TO_DOUBLE_RIDGE = 280.0

        model%start_day = start_day
        model%SGS = emergence
        model%mid_anthesis = model%SGS + SGS_TO_MID
        model%EGS = model%mid_anthesis + MID_TO_EGS
        model%double_ridge = model%SGS + EMERGENCE_TO_DOUBLE_RIDGE
        model%Astart = model%mid_anthesis - 200.0
        model%Aend = model%EGS

        model%canopy_f_phen_points = reshape( (/ model%SGS, 0.2, &
                                               & model%double_ridge, 1.0, &
                                               & model%mid_anthesis, 1.0, &
                                               & model%EGS, 0.2 /), &
                                            & shape(model%canopy_f_phen_points))
        model%canopy_f_phen_before = 0.0
        model%canopy_f_phen_after = 0.0

        model%leaf_f_phen_points = reshape( (/ model%Astart, 1.0, &
                                             & model%mid_anthesis + 100.0, 1.0, &
                                             & model%mid_anthesis + 525.0, 0.7, &
                                             & model%Aend, 0.0 /), &
                                          & shape(model%leaf_f_phen_points))
        model%leaf_f_phen_before = 0.0
        model%leaf_f_phen_after = 0.0

        ! TODO: what value should LAI be outside of the growing season?
        model%LAI_points = reshape( (/ model%SGS, 0.1, &
                                     & model%double_ridge, 0.1, &
                                     & model%mid_anthesis, 1.0, &
                                     & model%EGS, 0.2 /), &
                                  & shape(model%LAI_points))
        model%LAI_before = 0.0
        model%LAI_after = 0.0
    end function do3se_create_thermal_time_model

    ! =========================================================================
    ! Accumulate thermal time according to the properties of *model*.
    !
    ! If *day* is on or after the starting day of the model, then thermal time
    ! will be accumulated.  *thermal_time* is incremented by *tmean* above a
    ! threshold of 0 degrees - *thermal_time* will never decrease.
    ! =========================================================================
    pure subroutine do3se_accumulate_thermal_time(model, day, tmean, thermal_time)
        ! Inputs
        type(ThermalTimeModelType), intent(in) :: model     ! Thermal time model
        integer, intent(in) :: day  ! Day of year
        real, intent(in) :: tmean   ! Mean daily temperature (degrees C)
        ! Input/output
        real, intent(inout) :: thermal_time

        if (day >= model%start_day) then
            thermal_time = thermal_time + max(0.0, tmean)
        end if
    end subroutine do3se_accumulate_thermal_time

    pure function thermal_time_canopy_f_phen(model, thermal_time) result (f_phen)
        use do3se_utils, only: polygonal_chain

        ! Inputs
        type(ThermalTimeModelType), intent(in) :: model
        real, intent(in) :: thermal_time
        ! Output
        real :: f_phen

        f_phen = polygonal_chain( model%canopy_f_phen_points, &
                                & model%canopy_f_phen_before, &
                                & model%canopy_f_phen_after, &
                                & thermal_time )
    end function thermal_time_canopy_f_phen

    pure function thermal_time_leaf_f_phen(model, thermal_time) result (f_phen)
        use do3se_utils, only: polygonal_chain

        ! Inputs
        type(ThermalTimeModelType), intent(in) :: model
        real, intent(in) :: thermal_time
        ! Output
        real :: f_phen

        f_phen = polygonal_chain( model%leaf_f_phen_points, &
                                & model%leaf_f_phen_before, &
                                & model%leaf_f_phen_after, &
                                & thermal_time )
    end function thermal_time_leaf_f_phen

    pure function thermal_time_LAI(model, thermal_time) result (LAI)
        use do3se_utils, only: polygonal_chain

        ! Inputs
        type(ThermalTimeModelType), intent(in) :: model
        real, intent(in) :: thermal_time
        ! Output
        real :: LAI

        LAI = polygonal_chain( model%LAI_points, &
                             & model%LAI_before, &
                             & model%LAI_after, &
                             & thermal_time )
    end function thermal_time_LAI

end module DO3SE_thermal_time
