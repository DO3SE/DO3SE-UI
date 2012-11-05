module Parameters

    ! SMD soil texture parameters
    type SoilType
        ! SWC constant b
        real :: soil_b
        ! Field capacity (m3/m3)
        real :: Fc_m
        ! Water potential at air entry (MPa)
        real :: SWP_AE
        ! Saturated soil conductance (s-2 MPa-1 mm-1)
        real :: Ksat
    end type SoilType

    ! Commonly used soil textures
    ! ---------------------------
    ! Sandy loam
    type(SoilType), parameter :: SOIL_SANDY_LOAM = SoilType(soil_b = 3.31, &
                                                            Fc_m = 0.16, &
                                                            SWP_AE = -0.00091, &
                                                            Ksat = 0.0009576)
    ! Silt loam
    type(SoilType), parameter :: SOIL_SILT_LOAM  = SoilType(soil_b = 4.38, &
                                                            Fc_m = 0.26, &
                                                            SWP_AE = -0.00158, &
                                                            Ksat = 0.0002178)
    ! Loam
    type(SoilType), parameter :: SOIL_LOAM       = SoilType(soil_b = 6.58, &
                                                            Fc_m = 0.29, &
                                                            SWP_AE = -0.00188, &
                                                            Ksat = 0.0002286)
    ! Clay loam (Ksat estimated)
    type(SoilType), parameter :: SOIL_CLAY_LOAM  = SoilType(soil_b = 7.00, &
                                                            Fc_m = 0.37, &
                                                            SWP_AE = -0.00588, &
                                                            Ksat = 0.00016)

    type OptionsType
        ! Method for calculating SMD/SWP/SWC:
        !   "disabled", "P-M", "input SWP", "input SWC"
        character(len=16) :: SMD_method = "disabled"
        ! Method for incorporating SMD effect into stomatal conductance:
        !   "disabled", "fSWP exp", "fSWP linear", "fLWP SS", "fLWP non-SS",
        !   "fPAW"
        character(len=16) :: SWP_method = "disabled"
        ! Soil texture for SMD
        !   "sandy loam", "silt loam", "loam", "clay loam", "custom"
        character(len=16) :: soil_texture = "silt loam"
    end type OptionsType

    !==========================================================================
    ! Site-specific parameters
    !==========================================================================

    real, public, save  :: Rsoil = 100      ! Soil resistance in (s/m)

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
    real, public, save  :: Ksat = 0.0002178     ! Saturated soil conductance (s-2 MPa-1 mm-1)
                                                !  - sandy loam = 0.0009576
                                                !  - silt loam  = 0.0002178
                                                !  - loam       = 0.0002286
                                                !  - clay loam  = 0.00016 (estimated)
    ! New-style soil parameters, defaulting to "silt loam"
    type(SoilType) :: soil = SOIL_SILT_LOAM

    ! Measurement heights
    real, public, save :: uzR = 25      ! Windspeed measurement height (m)
    real, public, save :: O3zR = 25     ! Ozone concentration measurement height (m)
    real, public, save :: xzR = 25      ! "Other" measurement height (m)
    real, public, save :: D_meas = 0.5  ! Soil water measurement depth (m)
    
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
    public :: Derive_O3_d_zo


    !==========================================================================
    ! Vegetation-specific parameters
    !==========================================================================

    real, public, save :: T_min = 0    ! oC min temp for g
    real, public, save :: T_opt = 21   ! oC opt temp for g
    real, public, save :: T_max = 35   ! oC max temp for g

    real, public, save :: VPD_min = 3.25    ! VPD for min g
    real, public, save :: VPD_max = 1.0     ! VPD for max g
    real, public, save :: VPD_crit = 1000   ! Critical daily VPD sum (kPa)
    
    real, public, save :: SWP_min = -1.25   ! SWP for min g
    real, public, save :: SWP_max = -0.05   ! SWP for max g

    ! Boundary gs values
    real, public, save :: gmax = 148        ! mmol O3 m^-2 PLA s^-1
    real, public, save :: gmorph = 1.0      ! sun/shade leaf morphology modifier
    real, public, save :: fmin = 0.13       ! minimum gs

    real, public, save :: albedo = 0.12     ! 0.2 for crops
                                            ! 0.12 for needle leaf trees
                                            ! 0.14 for moorland
                                            ! 0.16 for broad leaf trees
    
    real, public, save :: root = 1.2        ! root depth (m)
    real, public, save :: h = 25            ! Canopy height (m)
    real, public, save :: zo                ! Roughness length (m)
    real, public, save :: d                 ! Displacement height (m)

    ! Growing season
    integer, public, save :: SGS = 121      ! Start of bulk canopy growth period
    integer, public, save :: EGS = 273      ! End of bulk canopy growth period

    ! Leaf area index
    real, public, save :: LAI_a = 0.0       ! First LAI point (at SGS)
    real, public, save :: LAI_b = 4.0       ! Second LAI point
    real, public, save :: LAI_c = 4.0       ! Third LAI point
    real, public, save :: LAI_d = 0.0       ! Last LAI point (at EGS)
    real, public, save :: LAI_1 = 30        ! Period from LAI_a to LAI_b
    real, public, save :: LAI_2 = 30        ! Period from LAI_c to LAI_d

    ! fphen polygon (see Calc_fphen in phenology.f90)
    real, public, save :: fphen_limA = 0    ! Start of soil water limitation
    real, public, save :: fphen_limB = 0    ! End of soil water limitation
    real, public, save :: fphen_a = 0.0     ! First fphen point (at SGS)
    real, public, save :: fphen_b = 1.0
    real, public, save :: fphen_c = 1.0     ! fphen during soil water limitation
    real, public, save :: fphen_d = 1.0
    real, public, save :: fphen_e = 0.0     ! Last fphen point (at EGS)
    real, public, save :: fphen_1 = 15      ! Period from fphen_a to fphen_b
    real, public, save :: fphen_2 = 0       ! Period from fphen_b to fphen_c
    real, public, save :: fphen_3 = 0       ! Period from fphen_c to fphen_d
    real, public, save :: fphen_4 = 20      ! Period from fphen_d to fphen_e


    ! leaf fphen polygon
    real, public, save :: Astart = 121      ! Start of upper leaf growth period
    real, public, save :: Aend = 273        ! End of upper leaf growth period
    real, public, save :: leaf_fphen_a = 0.0 ! First fphen point (at Astart)
    real, public, save :: leaf_fphen_b = 1.0 ! Second fphen point (plateau)
    real, public, save :: leaf_fphen_c = 0.0 ! Last fphen point (at Aend)
    real, public, save :: leaf_fphen_1 = 15 ! Time from leaf_fphen_a to leaf_fphen_b
    real, public, save :: leaf_fphen_2 = 30 ! Time from leaf_fphen_b to leaf_fphen_c

    real, public, save :: cosA = 0.5        ! A = mean leaf inclination (60 degs)
    real, public, save :: f_lightfac = 0.006 ! single leaf flight coefficient
                                            
    real, public, save :: Rext = 2500       ! external plant cuticle resistance in s/m
    real, public, save :: Rinc_b = 14       ! Rinc co-efficient

    real, public, save :: Lm = 0.05         ! Leaf dimension (m)
    real, public, save :: Y = 1.6           ! Threshold (Y) in AFstY, nmol O3 m-2 s-1

    ! Photosynthesis estimation parameters
    real, public, save :: g_sto_0 = 50000   ! Conductance with closed stomata (umol m-2 s-1)
    real, public, save :: m = 7.65          ! Species-specific sensitivity/fudge-factor
    real, public, save :: V_cmax_25 = 70.03 ! Maximum catalytic rate at 25C (umol m-2 s-1)
    real, public, save :: J_max_25 = 163.05 ! Maximum rate of electron transport at 25C (umol m-2 s-1)

    integer, public, save :: ttime_sowing = 0      ! Day of year to start counting thermal time
    real, public, save :: ttime_emergence = 0   ! Thermal time before emergence (degree days till SGS)

    ! Starting point for new options handling
    type(OptionsType), public, save :: options

    public :: Derive_d_zo

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

    !==========================================================================
    ! Derive the displacement height and roughness length from the height of 
    ! the canopy.
    !==========================================================================
    subroutine Derive_d_zo()
        d = h * 0.7
        zo = h * 0.1
    end subroutine Derive_d_zo

    !==========================================================================
    ! Read parameters from an open file, using a "parameters" namelist.
    !==========================================================================
    subroutine load_parameters(paramunit)
        use do3se_utils, only: die
        integer, intent(in) :: paramunit
        namelist /parameters/ Rsoil, &
                            & uzR, O3zR, xzR, D_meas, u_h, O3_h, &
                            & lat, lon, elev, &
                            & T_min, T_opt, T_max, &
                            & VPD_min, VPD_max, VPD_crit, &
                            & SWP_min, SWP_max, &
                            & gmax, gmorph, fmin, albedo, root, h, SGS, EGS, &
                            & LAI_a, LAI_b, LAI_c, LAI_d, LAI_1, LAI_2, &
                            & fphen_limA, fphen_limB, &
                            & fphen_a, fphen_b, fphen_c, fphen_d, fphen_e, &
                            & fphen_1, fphen_2, fphen_3, fphen_4, &
                            & Astart, Aend, leaf_fphen_a, leaf_fphen_b, &
                            & leaf_fphen_c, leaf_fphen_1, leaf_fphen_2, &
                            & cosA, f_lightfac, Rext, Rinc_b, Lm, Y, &
                            & g_sto_0, m, V_cmax_25, J_max_25, &
                            & ttime_sowing, ttime_emergence, &
                            & options, soil
        read(unit=paramunit, nml=parameters)

        !
        ! Process options
        !

        select case (options%soil_texture)
            case ("sandy loam")
                soil = SOIL_SANDY_LOAM
            case ("silt loam")
                soil = SOIL_SILT_LOAM
            case ("loam")
                soil = SOIL_LOAM
            case ("clay loam")
                soil = SOIL_CLAY_LOAM
            case ("custom")
                ! Do nothing; soil%* should have been set manually
            case default
                call die("unrecognised options%soil_texture: " // options%soil_texture)
        end select

        ! TODO: replace all instances of these variables
        soil_b = soil%soil_b
        Fc_m = soil%Fc_m
        SWP_AE = soil%SWP_AE
        Ksat = soil%Ksat

        print *, soil_b, Fc_m, SWP_AE, Ksat
    end subroutine load_parameters

end module Parameters
