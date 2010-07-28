module Params_Site

    real, public, save  :: Rsoil = 200      ! Soil resistance in (s/m)

    ! Soil properties all set based on "Soil texture"
    real, public, save  :: soil_b = 4.38        ! SWC constant b
                                                !  - sandy loam = 3.31
                                                !  - silt loam  = 4.38
                                                !  - loam       = 6.58
                                                !  - clay loam  = 7.00
    real, public, save  :: Fc_m = 0.26          ! Field capacity (m^3/m^3)
                                                !  - sandy loam = 0.16
                                                !  - silt loam  = 0.26
                                                !  - loam       = 0.29
                                                !  - clay loam  = 0.37
    real, public, save  :: SWP_AE = -0.00158    ! Water potential at air entry (MPa)
                                                !  - sandy loam = -0.00091
                                                !  - silt loam  = -0.00158
                                                !  - loam       = -0.00188
                                                !  - clay loam  = -0.00588

    ! Measurement heights
    real, public, save :: uzR = 25      ! Windspeed measurement height (m)
    real, public, save :: O3zR = 25     ! Ozone concentration measurement height (m)
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
    real, public, save :: lat = 50      ! Latitude (degrees)
    real, public, save :: lon = 0       ! Longitude (degrees)
    real, public, save :: elev = 0      ! Elevation (m)

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
    ! Derive the displacement height (d) and roughness length (zo) of the 
    ! vegetation under the O3 measurement based on its height
    !==========================================================================
    subroutine Derive_O3_d_zo()
        O3_d = O3_h * 0.7
        O3_zo = O3_h * 0.1
    end subroutine Derive_O3_d_zo

end module Params_Site
