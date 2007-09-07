module Params_Site

    real, public, save  :: Rsoil = 200      ! Soil resistance in (s/m)

    ! Soil properties all set based on "Soil texture"
    real, public, save  :: soil_BD = 1.3    ! Soil bulk density (g/cm^3)
    real, public, save  :: soil_a = -5.5    ! SWC constant a - coarse = -4,
                                            ! medium = -5.5, fine = -7
    real, public, save  :: soil_b = -3.3    ! SWC constant b - coarse = -2.3, 
                                            ! medium = -3.3, fine = -5.4
    real, public, save  :: Fc_m = 0.193     ! Field capacity (m^3/m^3)

    ! Measurement heights
    real, public, save :: uzR = 25      ! Windspeed measurement height (m)
    real, public, save :: czR = 25      ! Ozone concentration measurement height (m)
    real, public, save :: xzR = 25      ! "Other" measurement height (m)
    
    ! Properties of vegetation over which windspeed is measured
    real, public, save :: u_h = 25      ! Canopy height (m)
    real, public, save :: u_d           ! Canopy displacement height (m)
    real, public, save :: u_zo          ! Canopy roughness length

    ! Properties of vegetation over which O3 concentration is measured
    real, public, save :: O3_h = 25     ! Canopy height (m)
    real, public, save :: O3_d          ! Canopy displacement height (m)
    real, public, save :: O3_zo         ! Canopy roughness length

    ! Geographical location
    real, public, save :: lat           ! Latitude (degrees)
    real, public, save :: lon           ! Longitude (degrees)
    real, public, save :: elev          ! Elevation (m)

    public :: Derive_Windspeed_d_zo
    public :: Copy_Windspeed_h_d_zo
    public :: Derive_O3_d_zo
    public :: Copy_O3_h_d_zo

contains

    !==========================================================================
    ! Derive the displacement height (d) and roughness length (zo) of the 
    ! vegetation under the windspeed measurement based on its height
    !==========================================================================
    subroutine Derive_Windspeed_d_zo()
        u_d = u_h * 0.7
        u_zo = u_h * 0.1
    end subroutine Derive_Windspeed_d_zo

    !==========================================================================
    ! Copy height, displacement height and roughness length from the 
    ! vegetation parameters.  Use this if the wind speed measurements are over
    ! the same vegetation as the flux model is for.
    !==========================================================================
    subroutine Copy_Windspeed_h_d_zo()
        use Params_Veg, only: h, d, zo
        u_h = h
        u_d = d
        u_zo = zo
    end subroutine Copy_Windspeed_h_d_zo

    !==========================================================================
    ! Derive the displacement height (d) and roughness length (zo) of the 
    ! vegetation under the O3 measurement based on its height
    !==========================================================================
    subroutine Derive_O3_d_zo()
        u_d = u_h * 0.7
        u_zo = u_h * 0.1
    end subroutine Derive_O3_d_zo

    !==========================================================================
    ! Copy height, displacement height and roughness length from the 
    ! vegetation parameters.  Use this if the O3 measurements are over the same 
    ! vegetation as the flux model is for.
    !==========================================================================
    subroutine Copy_O3_h_d_zo()
        use Params_Veg, only: h, d, zo
        u_h = h
        u_d = d
        u_zo = zo
    end subroutine Copy_O3_h_d_zo

end module Params_Site
