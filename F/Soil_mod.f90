module Soil_mod
    real :: PWP        ! Calculated PWP in m3/3
    real :: ASW        ! Calculated ASW in m3/m3
    real :: Sn_star    ! Calculated Sn* in m3/m3
    real :: Sn         ! soil Water storage capacity
    real :: Sn_1       ! soil water storage capacity of previous day
    real :: per_vol    ! % volumetric water content
    real :: SMD        ! soil moisture deficit in mm
    real :: SWP        ! Soil water potential in MPa
    real :: WC         ! water content
    real :: precip     ! Previous day's total precipitation
    real :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations

    integer :: hour_count, hour_count_1, hour_count_2, hour_count_3, &
               hour_count_4, hour_count_5

    integer :: current_dd   ! Current day of the year - used for 
                            ! finding when the day changes

contains

    subroutine initialize()
        use Params_Site_mod, only: &
            Rsoil, soil_BD, soil_a, soil_b, Fc_m
        use Params_Veg_mod, only: &
            SWP_min, SWP_max

        ! Calculate Wstar
        PWP = soil_BD*((SWP_min/(soil_a*(0.01)))*1000)**(1/soil_b)
        ASW = Fc_m - PWP
        Sn_star = ASW

        ! Initialise other variables
        SWP         = (soil_a*0.01)*((Fc_m/soil_BD))**soil_b/1000
        Sn_1        = Sn_star
        WC          = Fc_m - PWP
        per_vol     = (Fc_m + PWP) * 100 
        fSWP        = 1


        
        
    end subroutine initialize

    subroutine Calc_precip()
        use Inputs_mod, only: dd, precip_in => precip
        use Variables_mod, only: dd_prev

        real, save :: precip_dd

        if ( dd == dd_prev ) then
            ! Same day, accumulate (converts mm to m)
            precip_dd = precip_dd + (precip_in/1000)
        else
            ! Next day, store and reset
            precip = precip_dd
            precip_dd = precip_in/1000
        endif
    end subroutine Calc_precip

    subroutine Calc_SMD()
        use Inputs_mod, only: dd
        use Variables_mod, only: dd_prev

        ! Only run the calculation if the day is over
        if ( dd /= dd_prev ) then

        endif
    end subroutine Calc_SMD

end module Soil_mod
