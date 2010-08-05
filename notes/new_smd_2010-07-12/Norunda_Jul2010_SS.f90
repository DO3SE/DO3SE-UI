	Program DOSE

! final code - no, really.  Based on Interface code, SEP 09.  Including Idiff, Idir calcs
! Calculates "canopy scale" Ra, Rb, Rsur and Vd and leaf AFstY using local EMEP
! met data

! =========================================
! Imported local variables, i.e. input data
! =========================================

integer :: mm      ! month
integer :: mdd     ! day of month
integer :: dd      ! day of year
integer :: hr      ! hour of day
real :: Ts_c       ! surface air temperature in oC
real :: ustar      ! Friction velocity (m/s)
real :: VPD        ! Vapour pressure deficit (kPa)
real :: precip     ! Precipitation (mm)s
real :: uh         ! Windspeed at top of canopy (m/s)
real :: O3_nmol_m3 ! Canopy ozone concentration (nmol/m3)
real :: O3_ppb_zR  ! Ozone concentration at observation height (ppb)
real :: O3_ppb     ! canopy height O3 in ppb (for AOT40 calculation)
real :: Rn_J       ! Net radiation (J m-2 h-1)
real :: P_atm	   ! Atmospheric pressure (Pa)
real :: PAR 	   ! Photosynthetically active radiation (micromol m-2 s-1)

! site = Norunda

real, parameter :: lat = 60.08      ! To match interface 
real, parameter :: lon = 0      ! To match interface 


! ====================================================
! Physical constants required for Ra & Rb calculations
! ====================================================

! von Karmans constant (k) = 0.41
! specific heat of air at constant pressure for dry air (cp, J/Kg/K) = 1005
! gravitational acceleration (g, m/s) = 9.8
! height of zref, 50m in EMEP model(O3z, m) = 25
! kinetic viscosity of air (v, m2/s at 20oC) = 0.000015
! molecular diffusivity of O3 in air relative, &
!                                 to water vapour (DO3, m2/s) = 0.000015
! Prandtl Number (Pr, -) = 0.72

real, parameter :: k=0.41

integer, parameter :: cp=1005
real, parameter :: g=9.8
real, parameter :: czR=25      ! Reference height for O3 concentration
real, parameter :: uzR=25      ! Reference height for wind speed

real, parameter :: v=0.000015
real, parameter :: DO3=0.000015  !molecular diffusivity for ozone at 20degC
real, parameter :: DH2O=0.000025 !molecular diffusivity for water at 20degC
real, parameter :: Pr=0.72
real, parameter :: h=25             ! Canopy height
real, parameter :: zo=h*0.1         ! roughness length (h*0.1)
real, parameter :: d=h*0.7          ! displacement height (h*0.7)

integer :: i, max_lines, ios

! ============================
! Calculated Ra & Rb variables
! ============================


real :: Ra_u         ! Atmospheric resistance for windspeed calculations (s/m)
                     ! Also used in SMD calcs. as assumed met variables
                     ! will be measured at same height (e.g. VPD and wind speed)
real :: Ra_O3        ! Atmospheric resistance for ozone calculations (s/m)
real :: uzh          ! Wind speed at top of canopy (i.e. h) (m/s)
                     ! N.B. Windseepd goes to zero at (d + zo) 
real :: Rb           ! Quasi-laminar boundary layer resistance (s/m)
real :: RbH2O        ! Quasi-laminar boundary layer resistance for water (s/m)


! =========================
! SMD calculation variables
! =========================

real :: Ei_hr      ! Hourly intercepted evaporation
real :: Es_hr      ! Hourly soil surface evaporation
real :: Et_hr      ! hourly canopy transpiration
real :: AEt_hr     ! Hourly actual transpiration - product of canopy transpiration and soil evaporation
real :: PEt_hr     ! Hourly potential transpiration

real :: ASW        ! Calculated ASW in m3/m3
real :: Sn_star    ! Calculated Sn* in m3/m3
real :: Sn         ! soil Water storage capacity
real :: Sn_diff    ! change in soil water over a day m3/m3
real :: trans_diff ! soil water input or output m
!real :: Sn_1       ! soil water storage capacity of previous day
real :: per_vol    ! % volumetric water content
real :: SMD        ! soil moisture deficit in mm - total amount of water required to recharge root zone
!real :: WD         ! water deficit m/m  - water deficit per meter of root zone
real :: SWP        ! Soil water potential in MPa
!real :: SWPcomp_a  ! SWP component A
!real :: SWPcomp_b  ! SWP component B
!real :: WC         ! water content

real :: precip_dd  ! cumulated daily precipitation
real :: precip_use ! daily precipitation used in calculations
real :: P_input    ! precipitaion input to soil minus canopy interception

real :: Ei_dd      ! cumulated daily intercepted evaporation
real :: Ei_use     ! daily intercepted evaporation used in calculations
real :: Es_dd      ! cumulative daily soil evaporation
real :: Es_use     ! daily soil evaporation used in calculations
real :: AEt_dd     ! cumulated daily actual transpiraton
real :: AEt_use    ! daily transpiration used in calculations
real :: PEt_dd     ! cumulated daily potential transpiraton
real :: PEt_use    ! daily potential used in calculations
real :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations
!real :: SWP_min_vol ! SWP min converted from MPa to m3/m3
real :: PWP_vol    ! PWP converted from MPa to m3/m3



!asdf
! =========================
! SMD - layers calculation variables
! =========================

real, parameter :: D0 = 0   ! surface
real, parameter :: D1 = 0.3 ! depth of soil layer 1
real, parameter :: D2 = 0.6 ! depth of soil layer 2
real, parameter :: D3 = 0.9 ! depth of soil layer 3
real, parameter :: D4 = 1.2 ! depth of soil layer 4 (must be bottom of root zone)

real, parameter :: D_meas = 0.5  !measurement depth in m of observed data


real :: L1                 ! layer thickness - layer 1
real :: L2                 ! layer thickness - layer 2
real :: L3                 ! layer thickness - layer 3
real :: L4                 ! layer thickness - layer 4

!calculate root fraction at depth D (in mm) using method from Baker et al (1996), 0.97 is an empirically derived constant for "trees"

real :: r_D1        ! root fraction at D1
real :: r_D2        ! root fraction at D2
real :: r_D3        ! root fraction at D3
real :: r_D4        ! root fraction at D4
real :: r_meas      ! root fraction at measured data depth


real :: P_input_meas ! P input to soil layer above measured data depth
real :: P_input_D1 !  precipitaion input to soil Layer 1
real :: P_input_D2 ! precipitaion input to soil Layer 2
real :: P_input_D3 !  precipitaion input to soil Layer 3
real :: P_input_D4 !  precipitaion input to soil Layer 4

!Transpiration fraction at each depth
real :: et_D1        !transpiration fraction at D1
real :: et_D2        !transpiration fraction at D2
real :: et_D3        !transpiration fraction at D3
real :: et_D4        !transpiration fraction at D4
real :: et_meas      ! tranpiration at measured data depth

! fraction of Et transfering to next layer down if Et_k exceeds SMD in soil layer
Real :: Et_D1_o
Real :: Et_D2_o
Real :: Et_D3_o
Real :: Et_D4_o



!real :: total_e_Dk        !sum of all transpiration fractions


! soil water storage at each depth

real :: Sn_D1
real :: Sn_D2
real :: Sn_D3
real :: Sn_D4
real :: Sn_meas

! change in water input/output at each depth
real :: Trans_diff_D1        
real :: Trans_diff_D2        
real :: Trans_diff_D3        
real :: Trans_diff_D4     
real :: Trans_diff_meas        

! change in soil water storage at each depth
real :: Sn_diff_D1
real :: Sn_diff_D2
real :: Sn_diff_D3
real :: Sn_diff_D4
real :: Sn_diff_meas

! SWP at each depth

real :: SWP_D1     
real :: SWP_D2
real :: SWP_D3
real :: SWP_D4
real :: SWP_meas

real :: SWP_effec  ! effective SWP experienced by plant, used to define pre-dawn potential
     

! SWD at each depth

real :: SMD_D1     
real :: SMD_D2     
real :: SMD_D3     
real :: SMD_D4    
real :: SMD_meas 

!calculate fSWp at depth D

real :: fSWP_D1     
real :: fSWP_D2     
real :: fSWP_D3     
real :: fSWP_D4     
real :: fSWP_effec !mean of layer fSWP

! calculate total Sn_diff based on total extraction from all soil layers
real :: sn_diff_layers
real :: trans_diff_layers



!====================================
!Leaf water potential (LWP) variables
!====================================

real :: LWP                     !leaf water potential (MPa)
real :: LWP_1                   !leaf water potential of previous hour (MPa)
real :: deltaLWP                !change in leaf water potential between hours
real :: fLWP                    !LWP limitation on gsto

real :: SWP_1                   !soil water potential of previous day

Real :: Rsr_D1                      !soil-root resistance in layer 1
Real :: Rsr_D2                      !soil-root resistance in layer 2
Real :: Rsr_D3                      !soil-root resistance in layer 3
Real :: Rsr_D4                      !soil-root resistance in layer 4
Real :: Rsr                      !soil-root resistance of all layers in parallel


Real :: Ks_D1                      !soil hydraulic conductivity in layer 1
Real :: Ks_D2                      !soil hydraulic conductivity in layer 2
Real :: Ks_D3                      !soil hydraulic conductivity in layer 3
Real :: Ks_D4                      !soil hydraulic conductivity in layer 4
Real :: Ks                         !Bulk soil hydraulic conductivity

real :: delta_t                 !change in time (h)
real :: delta_Et               !change in AEt between hours
real :: Et_hr_1                !previous hour's Et

real, parameter  :: K1 = 0.0000000000035 ! constant related to root density
real :: K1_D1               !root density parameter adjusted for root fraction in soil layer 1
real :: K1_D2               !root density parameter adjusted for root fraction in soil layer 2
real :: K1_D3               !root density parameter adjusted for root fraction in soil layer 3
real :: K1_D4               !root density parameter adjusted for root fraction in soil layer 4


!real, parameter  :: SWPsat = -0.004 !SWP at water saturation (MPa)

real, parameter  :: C  = 1                !Plant capacitance mm MPa-1
real, parameter  :: Rc = 0.42        ! storage/destorage hydraulic resistance MPa h mm-1
real, parameter  :: Rp = 5.3        !plant hydraulic resistance MPa h mm-1




! ====================
! Penman-Monteith variables
! ====================

real :: esat       ! satuarted water vapour pressure in Pa
real :: eact       ! actual water vapour pressure in Pa
real :: Tvir       ! virtual temperature in K
real :: delta      ! slope of vapour pressure curve (Pa C-1)
real :: lamda      ! latent heat of vapourisation (J kg -1)
real :: psychro    ! psychrometric constant
real :: Pair       ! air density (kg cm-3)
real :: Cair       ! heat capacity of moist air (J g-1 C-1)
real :: G_J        ! Soil heat flux (J m-2 h-1) 

real :: ET_1      ! PM calculation step
real :: ET_2      ! PM calculation step
real :: ET_3      ! PM AEt calculation (in mm/day converted to m/day by 1000)
real :: PET_3      ! PM PEt calculation (in mm/day coverted to m/day by 1000)

real :: Ei_1       ! PM Ei calculation step 1
real :: Ei_2       ! PM Ei calculation step 2
real :: Ei_3       ! PM Ei calculation step 3

real :: Es_1       ! PM Es calculation step 1
real :: Es_2       ! PM Es calculation step 2
real :: Es_3       ! PM Es calculation step 3
real :: t          ! fraction of available energy at soil surface - controlled by LAI
real :: Rn_J_g      ! radiaton available at soil surface (Rn_J * t)    
!real :: Es_G_J


real :: C_canopy   !coefficient of canopy transpiration for total AEt calculation
real :: C_soil     !coefficient of canopy transpiration for total AEt calculation

real :: SW_a        !equation component for caclulation of AEt coefficients - from Shuttleworht and Wallace (SW), 1985
real :: SW_s       !equation component for caclulation of AEt coefficients - from Shuttleworht and Wallace (SW), 1985
real :: SW_c       !equation component for caclulation of AEt coefficients - from Shuttleworht and Wallace (SW), 1985


real, parameter :: Psurf = 101325 ! standard atmospheric pressure in Pa
                                  ! Assumed air pressure in place of actual data


integer :: hour_count, hour_count_1, hour_count_2, hour_count_3, &
           hour_count_4, hour_count_5, hour_count_6

! =====================
! Rsur & go3 parameters
! =====================

real, parameter :: SGS = nint(((lat-50)*1.5)+105)  ! start of bulk canopy growth period
real, parameter :: EGS = nint(297-((lat-50)*2))    ! end of bulk canopy growth period

real, parameter :: Astart = SGS         ! start of upper leaf growth period
real, parameter :: Aend = EGS           ! end of upper leaf growth period

real, parameter :: LAI_max =  6.5       ! maximum LAI in m2/m2
real, parameter :: LAI_min = 6.5      ! minimum LAI in m2/m2 
real, parameter :: Ls = 0           ! days to go from min LAI in m2/m2 to max 
real, parameter :: Le = 0            ! days to go from max LAI in m2/m2 to min 

real, parameter :: gmax = 112         ! mmol O3 m-2 PLA s-1
real, parameter :: fmin = 0.2         ! minimum gs

real, parameter :: fphen_a = 0      ! fphen at SGS
real, parameter :: fphen_b = 0     ! fphen at Astart
real, parameter :: fphen_c = 1.0      ! fphen midway during season
real, parameter :: fphen_d = 0      ! fphen at Aend and EGS
real, parameter :: fphenS  = 20       ! period to fphen_c
real, parameter :: fphenE  = 20       ! period to fphen_d 


real, parameter ::  PI = 3.14159265358979312     ! pi
real, parameter ::  DEG2RAD = PI/180.0           ! Degrees -> Radians
real, parameter ::  nydays = 365                 ! no. days per year (365 or 366)
real, parameter ::  cosA    = 0.5                ! A = mean leaf inclination (60 deg.)
                                                 ! where it is assumed that leaf
  							       ! inclination has a spherical distribution

real, parameter :: albedo = 0.12                  ! 0.2 is value for crops, 
								 ! 0.12 for needle leaf trees, 
								 ! 0.16 for broad leaf trees
                                                 ! 0.14 for moorland
real, parameter :: PARfrac = 0.45                ! approximation to fraction (0.45
							       ! to 0.5) of total
                                                 ! radiation in PAR waveband (400-700nm)
real, parameter :: Wm2_uE  = 4.57                ! converts from W/m^2 to umol/m^2/s
real, parameter :: Wm2_2uEPAR= PARfrac * Wm2_uE  ! converts from W/m^2 to umol/m^2/s PAR
real, parameter :: f_lightfac = 0.006             ! single leaf flight co-efficient

real, parameter ::  T_min = 0        ! oC min temperature for g
real, parameter ::  T_opt = 20         ! oC opt temperature for g
real, parameter ::  T_max = 35        ! oC max temperature for g

real, parameter :: VPD_max = 0.8      ! VPD for max g
real, parameter :: VPD_min = 2.8      ! VPD for min g

! fswp = 1 for generic Med evergreen (use dummy values here and set fSWP = 1 later)
real, parameter :: SWP_max = -0.5    ! SWP for max g
real, parameter :: SWP_min = -1.5    ! SWP for min g
real, parameter :: PWP = -4          ! PWP (MPa) cut off - as threshold below which fswp - 0.01


!real, parameter :: seaP = 101.325     ! sea level presuure in kPa
real, parameter :: Rgs = 200        ! Soil resistance in s/m
real, parameter :: Rinc_b = 14        ! Rinc co-efficient
real, parameter :: Rext = 2500        ! external plant cuticle resistance in s/m
real, parameter :: Ts_k = 273.16      ! Conversion from ToC to T Kelvin

! ********************************************************************
! Soil water release curve constants; after Millthorpe & Moorby, 1974)
! ********************************************************************

!real, parameter :: soil_BD = 1.6    ! Soil bulk density (g/cm^3)
                                    ! coarse = 1.6, medium = 1.3, fine = 1.1
!real, parameter :: soil_a = -4      ! SWC constant a
                                    ! coarse = -4, medium = -5.5, fine = -7
!real, parameter :: soil_b = -2.3    ! SWC constant b
                                    ! coarse = -2.3, medium -3.3, fine = -5.4
!real, parameter :: Fc_m = 0.15      ! Field capacity(m3/m3)
                                    ! coarse = 0.15, medium = 0.27, fine = 0.43
!real, parameter :: root = 1.2       ! root depth, soil and species specific (m)

!real, parameter :: Lm = 0.05        ! Leaf dimension (m)
!real, parameter :: Y = 1.6          ! Threshold (Y) in AFstY, nmol O3 m-2 s-1

! ********************************************************************
! Soil water release curve constants; after Saxton et al 1984
! Soil sand, silt, clay contents based on BSS triangle (Ashman & Puri)
! soil textures: Coarse=sandy loam (70,20,10), medium=silt loam (10,80,10), fine=clay (20,20,60)
! Field capacities from Foth
! ********************************************************************


!real, parameter :: soil_a = -4      ! SWC constant a
                                    ! coarse = -4, medium = -5.5, fine = -7
!real, parameter :: soil_b = -2.3    ! SWC constant b
                                    ! coarse = -2.3, medium -3.3, fine = -5.4

!real, parameter :: soil_BD = 1.6    ! Soil bulk density (g/cm^3)
                                    ! coarse = 1.6, medium = 1.3, fine = 1.1
!real, parameter :: sand = 95        ! percentage sand content of soil
                                   ! Coarse=65 (45-85), Medium=25 (5-45), fine=25 (5-45)
!real, parameter :: clay = 5        !percentage clay content of soil
                                    !Coarse=12 (5-20), Medium=15 (5-25), fine=50 (40-60)

!real, parameter :: Fc_m = 0.16      ! Field capacity(m3/m3)
                                    ! coarse = 0.26, medium = 0.88, fine = 0.47
                                    ! Field capacities are set by SWP = -0.01 Mpa

!real, parameter :: root = 1.2       ! root depth, soil and species specific (m)

!real, parameter :: Lm = 0.07        ! Leaf dimension (m)
!real, parameter :: Y = 1.6          ! Threshold (Y) in AFstY, nmol O3 m-2 s-1

!saxton et al swp parameters

!real, parameter :: swp_a = -4.396
!real, parameter :: swp_b = -0.0715
!real, parameter :: swp_c = -0.000488
!real, parameter :: swp_d = -0.00004285
!real, parameter :: swp_e = -3.14
!real, parameter :: swp_f = -0.00222
!real, parameter :: swp_g = -0.00003484

! ********************************************************************
!Soil water release constants after Campbell (1985) with constants defined from
!experimental data by Tuzet et al (2003)

!***************************************************

real, parameter :: soil_BD = 1.6    ! Soil bulk density (g/cm^3)
                                    ! coarse = 1.6, medium = 1.3, fine = 1.1


real, parameter :: Fc_m = 0.26      ! Field capacity(m3/m3)
                                    ! coarse (sandy loam) = 0.14-0.19, medium (Loam) = 0.24-0.28, fine (silt loam) = 0.28-0.3
                                    !clay loam = 0.36-0.38
                                    ! Field capacities are set by SWP = -0.01 Mpa


real, parameter :: root = 1.2      ! root depth, soil and species specific (m)

real, parameter :: Lm = 0.006        ! Leaf dimension (m)
real, parameter :: Y = 1          ! Threshold (Y) in AFstY, nmol O3 m-2 s-1


!Campbell parameters

real, parameter :: soil_B = 4.38    !from Tuzet et al 2003
                                    !Sandy loam = 3.31, Silt loam = 4.38, Loam = 6.58
                                    !!clay loam = 7 (estimated)

real, parameter :: SWP_AE = -0.00158 ! water potential at air entry (MPa)
                                              ! sandy loam = -0.00091, silt loam, -0.00158, loam, -0.00188
                                              ! clay loam = -0.00588 (estimated)           

real, parameter :: SWC_sat = 0.4    ! saturated water content m3/m3.  This is always 0.4

Real, parameter :: Ksat = 0.0002178   ! Saturated soil conductance (s-2 MPa-1 m2)
                                              ! sandy loam = 0.0009576, silt loam, 0.0002178, loam, 0.0002286
                                              ! clay loam = 0.00016 (estimated)           



! =============================================
! Calculated deposition, Rsur and go3 variables
! =============================================

real :: SAI              ! Stand Area Indea m2/m2
real :: LAI              ! Leaf Area Index m2/m2

real :: Gsto             ! Mean stomatal conductance mmol O3 m-2 PLA s-1
real :: Gsto_1           ! Leaf stomatal conductance mmol O3 m-2 PLA s-1
real :: Gsto_c           ! Canopy stomatal conductance mmol O3 m-2 PLA s-1
real :: Gsto_PEt         ! Bulk stomatal conductance mmol O3 m-2 PLA s-1
				 ! assuming no soil water limit
real :: gO3              ! Upper leaf stomatal conductnce mmol O3 m-2 PLA s-1
real :: leaf_r           ! leaf resistance s/m

real :: fphen            ! phenology related bulk g
real :: flight           ! Canopy average gsto in relation to canopy light
real :: ftemp            ! temperate related g
real :: bt               ! ftemp variable
real :: fVPD             ! VPD related g
real :: Rsto             ! average canopy leaf stomatal resistance to O3 in s/m
real :: Rsto_1		 ! Leaf stomatal stomatal resistance to O3 in s/m
real :: Rsto_c		 ! Canopy stomatal stomatal resistance to O3 in s/m
real :: fSWP             ! SWP related g
real :: Rinc             ! In-canopy aerodynamic reistance
real :: Rsur             ! Surface resistance to ozone in s/m
real :: Ftot             ! Total ozone flux to vegetated surface in nmol O3 m-2 PLA s-1

real :: leaf_fphen       ! phenology related to leaf g
real :: leaf_flight      ! light related g
real :: leaf_rb          ! leaf level rb in s/m
real :: leaf_gb          ! leaf level gb in m/s


! flight variables

real :: lonm
real :: f
real :: e
real :: lc
real :: t0
real :: hs
real :: dec
real :: m
real :: pPARdir
real :: pPARdif
real :: pPARtotal
real :: st
real :: fPARdir
real :: fPARdif
real :: PARdir
real :: PARdif
real :: LAIsun
real :: LAIshade
real :: PARshade
real :: PARsun
real :: Flightsun
real :: Flightshade
!real :: LAIsunfrac
real :: sinB            ! B = solar elevation angle complement
                        ! of zenith angle
!real :: sunLAI          ! sunlit LAI
!real :: f_shade         ! shade-leaf contribution to f_light

real :: Vd     		! Deposition velocity of ozone (m/s)
real :: Fst   		! Upper leaf stomatal ozone flux (nmol O3 m-2 PLA s-1)
real :: AFstY 		! Accumulated stomatal flux above a threshold Y (mmol O3 m-2 PLA)
real :: OT40   		! Ozone over 40 ppb over fphen period (ppm)
real :: AOT40  		! AOT40 over bulk canopy growth period (ppm.hrs)



! ======================
! Read in data from file
! ======================

max_lines = 400000


open (unit=9, file="norunda 1999", &
       status="old", action="read", position="rewind")

open (unit=8, file="norunda 1999 output", &
       status="replace", action="write", position="rewind")


! ****************************
! Initialize variables for SWP
! ****************************

   hour_count        = 0
   hour_count_1      = 0
   hour_count_2      = 0
   hour_count_3      = 0
   hour_count_4      = 0
   hour_count_5      = 0

   Precip_dd         = 0
   precip_use        = 0
   P_input           = 0
   P_input_D1        = 0
   P_input_D2        = 0

   Ei_use            = 0
   AEt_use           = 0
   AEt_dd            = 0
   PEt_use           = 0
   PEt_dd            = 0
   Ei_dd             = 0

   Es_dd             = 0
   Es_use            = 0

   SMD               = 0
!   WC                = 0
   Sn_diff           = 0
   trans_diff        = 0

! ****************************
! Initialize variables for SWP - Layers
! ****************************

 hour_count_6         = 0

   


! *******************************

! ===============================
! Calculate Wstar for medium soil
! ===============================

!SWPcomp_a = (exp(swp_a+(swp_b*clay)+(swp_c*sand**2)+(swp_d*sand**2*clay))*100)
!SWPcomp_b = swp_e+(swp_f*clay**2)+(swp_g*sand**2)+(swp_g*sand**2*clay)

!PWP = (((-SWP_min)*1000)/SWPcomp_a)**(1/SWPcomp_b)

!SWP_min_vol = 1/(((SWP_min/SWP_AE)**(1/soil_B))/SWC_sat)
PWP_vol = 1/(((PWP/SWP_AE)**(1/soil_B))/SWC_sat)

ASW = (Fc_m - PWP_vol) * root
Sn_star = Fc_m



! Initialize SWP variables, MPa (according to soil specific attributes)
! old swp curve (soil_a*0.01)*((FC_m/soil_bd))**soil_b/1000
! Saxton curve = -(SWPcomp_a*(FC_m**SWPcomp_b))/1000  
   

   SWP         = SWP_AE*((SWC_sat/FC_m)**soil_B)
   Sn          = Sn_star
!   WC          = Fc_m - SWP_min_vol
   Per_vol     = Fc_m * 100 
   fSWP        = 1
   fLWP        = 1


! Initialise variables for SWP - Layers

 L1 = D1 - D0
 L2 = D2 - D1
 L3 = D3 - D2
 L4 = D4 - D3

 r_D1 = (1-(0.97**(D1*100)))-(1-(0.97**(D0*100)))
 r_D2 = (1-(0.97**(D2*100)))-(1-(0.97**(D1*100)))
 r_D3 = (1-(0.97**(D3*100)))-(1-(0.97**(D2*100)))
 r_D4 = (1-(0.97**(D4*100)))-(1-(0.97**(D3*100)))

 r_meas = (1-(0.97**(D_meas*100)))-(1-(0.97**(D0*100)))


 SWP_D1        = SWP_AE*((SWC_sat/FC_m)**soil_B)      
 SWP_D2        = SWP_AE*((SWC_sat/FC_m)**soil_B)
 SWP_D3        = SWP_AE*((SWC_sat/FC_m)**soil_B)
 SWP_D4        = SWP_AE*((SWC_sat/FC_m)**soil_B)
 SWP_meas      = SWP_AE*((SWC_sat/FC_m)**soil_B)

 SWP_Effec = ((SWP_D1*r_D1)+(SWP_D2*r_D2)+(SWP_D3*r_D3)+(SWP_D4*r_D4))/ (r_D1 + r_D2 + r_D3 + r_D3)

 Sn_D1          = Sn_star
 Sn_D2          = Sn_star
 Sn_D3          = Sn_star
 Sn_D4          = Sn_star
 Sn_meas         = Sn_star

 SMD_D1         = 0
 SMD_D2         = 0
 SMD_D3         = 0
 SMD_D4         = 0
 SMD_meas         = 0

 fSWP_D1        = 1
 fSWP_D2        = 1
 fSWP_D3        = 1
 fSWP_D4        = 1


 Sn_diff_D1     = 0
 Sn_diff_D2     = 0
 Sn_diff_D3     = 0
 Sn_diff_D4     = 0
 Sn_diff_meas     = 0

 Trans_diff_D1  = 0
 Trans_diff_D2  = 0
 Trans_diff_D3  = 0
 Trans_diff_D4  = 0
 Trans_diff_meas  = 0

 et_D1          = 0
 et_D2          = 0
 et_D3          = 0
 et_D4          = 0
 et_meas        = 0

print *, Sn_star, SWP, Sn


! Initialize other variables

   AFstY      = 0
   Fst        = 0
!   LAIsunfrac = 0
   AOT40      = 0
   OT40       = 0

do i=1, max_lines

read(unit=9, fmt=*, iostat=ios) mm, mdd, dd, hr, Ts_c, VPD, &
                                precip, uh, O3_ppb_zR, Rn_J, P_atm, PAR

if (ios>0) then
print *, "Error during opening"
exit

else if (ios<0) then
print *, "End of file reached :o)"
exit

end if


! ===============================
! Stops wind speed from being zero and allowing leaf level r_b to be estimated
! ===============================

   if (uh <= 0 ) then

     uh = 0.001

     else if (uh > 0) then

     uh = uh

   end if


! =========================================
! Calculate ustar (m/s)
! =========================================

ustar = (uh*k) / log((uzR-d)/(zo))


! =========================================
! Calculate Ra, atmospheric resistance, s/m
! =========================================
! Assuming neutral stability

! Make sure calculation works even if uzR below d+zo

if (uzR < d+zo) then 

Ra_u = 1/(k*ustar)*(log(((zo + d)-d)/(h-d)))

else if (uzR >= d + zo) then

Ra_u = 1/(k*ustar)*(log((uzR-d)/(h-d)))

end if

! ===============================================
! Calculate Uzh, wind speed at top of canopy, m/s
! ===============================================


Uzh = (ustar/k) * log((h-d)/zo)



! ==========================================================
! Calculate Rb, quasi-laminar boundary layer resistance, s/m
! ==========================================================


Rb = (2/(k*ustar)) * ((v/DO3/Pr)**(0.6666666666666))
RbH2O = (2/(k*ustar)) * ((v/DH2O/Pr)**(0.6666666666666))


! ===============
! Calculate Rsur
! ===============




! =============
! Calculate LAI - not needed as use LAI from the GGM 
! =============


if (dd < SGS) then

  LAI = LAI_min

else if (dd >= SGS .and. dd < SGS+Ls) then

  LAI=(LAI_max-LAI_min)*((dd-SGS)/Ls)+LAI_min

else if (dd >= SGS+Ls .and. dd < EGS-Le) then

  LAI = LAI_max

else if (dd >= EGS-Le .and. dd < EGS) then

  LAI=(LAI_max-LAI_min)*((EGS-dd)/Le)+LAI_min

else if (dd >= EGS) then

  LAI = LAI_min

end if


! =============
! Calculate SAI - simple function used for now for grasses
! =============



SAI = LAI+1
  

! The code below is for crops, for forest trees SAI = 1 + LAI (placed at end of 
! code to over-ride crop code...)

!if (dd < SGS) then

!  SAI = LAI

! else if (dd >= SGS .and. dd < SGS+Ls) then

!  SAI = LAI+((5/3.5)-1)*LAI

! else if (dd > SGS+Ls .and. dd <= EGS) then

!  SAI = LAI + 1.5

! else if (dd > EGS) then

! SAI = LAI

! end if

! SAI = 1 + LAI     ! SAI for trees


! =====================================
! Calculate bulk canopy GSto (and Rsto)
! =====================================

! RSto = [(gmax*Fphen*Flight*max{fmin, (ftemp*fVPD*fSWP)})/41000]-1
! where 41000 converts from mmol m-2 s-1 to in m/s

! ================
! Calculate fphen
! ================

if (dd <= SGS) then
fphen = 0

else if (dd < Astart) then
fphen = fphen_a

else if (dd >= Astart .and. dd < Astart+fphenS ) then
fphen =  fphen_b + (fphen_c - fphen_b) * (dd-Astart)/fphenS

else if (dd >= Astart + fphenS .and. dd < Aend - fphenE ) then
fphen =  fphen_c

else if ( dd >= Aend - fphenE .and. dd < Aend ) then
fphen =  fphen_d + ( fphen_c - fphen_d) *(Aend - dd)/fphenE

else if (dd >= Aend .and. dd <= EGS) then
fphen = fphen_d

else if (dd > EGS) then
fphen = 0

end if



!fphen = 1    ! For CCE parameterisation (at the moment...after Rome meeting in 2007)

! ================
! Calculate Flight
! ================


! Calculate the longitudinal meridian
  lonm = nint(lon / 15.0) * 15.0

! Solar noon correction for day of year
      f = deg2rad * (279.575 + (0.9856 * dd))
      e = (-104.7 * sin(f) + 596.2 * sin(2 * f) + 4.3 * sin(3 * f) - 12.7 * sin(4 * f) &
           - 429.3 * cos(f) - 2.0 * cos(2 * f) + 19.3 * cos(3 * f)) / 3600

! Solar noon, with day of year and longitudinal correction
        LC = (lon - lonm) / 15.0
       t0 = 12.0 - LC - e

! Hour-angle of the sun
        hs = deg2rad * (15.0 * (hr - t0))

! Declination (radians)
   
	dec = deg2rad * (-23.4 * cos(deg2rad * (360.0 * ((dd + 10.0) / 365.0))))
	
      sinB = sin(deg2rad * (lat)) * sin(dec) + cos(deg2rad * (lat)) * cos(dec) * cos(hs)
     sinB = max(0.0, sinB)

! *****************************
! calculate PARsun and PARshade
! *****************************
! N.B. This part of the algorithm seems to produce the "floating underflow"

if (sinB > 0.0 .and. LAI > 0.0) then

            m = 1.0 / sinB

            ! Potential direct and diffuse PAR
            pPARdir = 600.0 * exp(-0.185 * (P_atm/Psurf) * m) * sinB
            pPARdif = 0.4 * (600.0 - pPARdir) * sinB
            pPARtotal = pPARdir + pPARdif

            ! Sky transmissivity (with PAR converted to W/m^2)
            ST = min(0.9, max(0.21, (PAR/4.57)/pPARtotal))

            fPARdir = (pPARdir/pPARtotal) * (1.0-((0.9-ST)/0.7)**(2.0/3.0))
            fPARdif = 1.0 - fPARdir

            PARdir = fPARdir * PAR
            PARdif = fPARdif * PAR

            LAIsun = (1.0 - exp(-0.5 * LAI / sinB)) * (2.0 * sinB)
            LAIshade = LAI - LAIsun

            PARshade = PARdif*exp(-0.5*(LAI**0.8))+0.07*PARdir*(1.1-(0.1*LAI))*exp(-sinB)
            PARsun = PARdir * 0.8 * (cosA/sinB) + PARshade

            ! TODO: does this need albedo?
            Flightsun = (1.0 - exp(-f_lightfac * PARsun))
            Flightshade = (1.0 - exp(-f_lightfac * PARshade))

            leaf_flight = (1.0 - exp(-f_lightfac * PAR))
            Flight = ((Flightsun * LAIsun) / LAI) + ((Flightshade * LAIshade) / LAI)
        else
            leaf_flight = 0.0
            Flight = 0.0
        end if


! N.B. Dave Simpson was using zen < 89.9 but this seemed to produce a
! floating underflow, if use < 88 the problem seems to be solved
! with no change to the results.

 ! sinB = cos(zen*DEG2RAD)    ! uses EMEP output zen to estimate sinB
                              ! ensures consistency between zen and &
                              ! Idrctt & Idfuse


 !  sunLAI = (1.0 - exp(-0.5*LAI/sinB) ) * sinB/cosA
 !  LAIsunfrac = sunLAI/LAI

    ! PAR flux densities evaluated using method of Norman (1982, p.79):
    ! "conceptually, 0.07 represents a scattering coefficient"


 !  PARshade = Idfuse * exp(-0.5*LAI**0.7) +  &
   !            0.07 * Idrctt  * (1.1-0.1*LAI)*exp(-sinB)

 !  PARsun = Idrctt *cosA/sinB + PARshade

    ! .. Convert units, and to PAR fraction and multiply by albedo...

!  PARshade = PARshade * Wm2_2uEPAR * ( 1.0 - albedo )
 ! PARsun   = PARsun   * Wm2_2uEPAR * ( 1.0 - albedo )

!else if (zen > 88 .or. LAI == 0 .or. Idrctt == 0) then

 ! sinB = 0
!  LAIsunfrac = 0
 ! PARshade = 0
 ! PARsun = 0

!end if

! ********************************
! calculate Flight and leaf_flight
! ********************************

!leaf_flight   = (1.0 - exp (-f_lightfac*PARsun) )
!f_shade       = (1.0 - exp (-f_lightfac*PARshade) )

!Flight        = LAIsunfrac * leaf_flight + (1.0 - LAIsunfrac) * f_shade

! ================
! Calculate ftemp
! ================

bt = (T_max-T_opt)/(T_opt-T_min)

ftemp = ((Ts_c-T_min)/(T_opt-T_min))*((T_max-Ts_c)/(T_max-T_opt))**bt
ftemp = max(ftemp, fmin)

!if (Ts_C > 20) then 
!ftemp = 1
!end if

! ===============
! Calculate fVPD
! ===============

fVPD = ((1-fmin)*(VPD_min-VPD)/(VPD_min-VPD_max))+fmin
fVPD = max(fVPD, fmin)

if (fVPD > 1) then
fvPD = 1
end if

!fVPD = 1


! =======================================
! Calculate LWP
! =======================================


K1_D1   = K1 * r_D1
K1_D2   = K1 * r_D2
K1_D3   = K1 * r_D3
K1_D4   = K1 * r_D4



ks_D1 = Ksat * ((SWP_AE/SWP_D1)**((3/soil_b)+2))
ks_D2 = Ksat * ((SWP_AE/SWP_D2)**((3/soil_b)+2))
ks_D3 = Ksat * ((SWP_AE/SWP_D3)**((3/soil_b)+2))
ks_D4 = Ksat * ((SWP_AE/SWP_D4)**((3/soil_b)+2))

ks = Ksat * ((SWP_AE/SWP)**((3/soil_b)+2))

Rsr_D1 = K1_D1 / (L1 * Ks_D1)
Rsr_D2 = K1_D2 / (L2 * Ks_D2)
Rsr_D3 = K1_D3 / (L3 * Ks_D3)
Rsr_D4 = K1_D4 / (L4 * Ks_D4)

Rsr = K1 / (Root * Ks)











! =======================================
! Calculate Gsto using previous days fSWP
! =======================================

! Leaf Gsto

Gsto_1 = gmax * fphen * leaf_flight * max(fmin, ftemp * fVPD * fLWP)   

! Mean Gsto

Gsto = gmax * fphen * flight * max(fmin, ftemp * fVPD * fLWP) 

!Estimate canopy Gsto from mean leaf Gsto

Gsto_c = Gsto * LAI


! ===================================================================
! Calculate Gsto for PEt calculation (i.e. assuming non-limiting SWP)
! ===================================================================

Gsto_PEt = gmax * fphen * flight * ftemp * fVPD * LAI	! in mmol O3 m-2 s-1

! Leaf Rsto

 if (Gsto_1 <= 0) then

   Rsto_1 = 100000.0         				! to allow for negligible Rsto

  else 

  Rsto_1 = 41000.0 / Gsto_1   		
					
  end if


! ===============================

! Mean Rsto

if (Gsto <= 0) then

     Rsto = 100000.0

   else 

     Rsto = 41000.0 / Gsto ! Gsto in s/m = Gsto * 41000, Rsto = 1 / Gsto

   end if

!Canopy Rsto 

if (Gsto_c <= 0) then

    Rsto_c = 100000.0

else 

    Rsto_c = 41000.0 / Gsto_c

end if 


!Potential canopy Rsto for PEt calculation

if (Gsto_PEt <= 0) then 

    Rsto_PEt = 100000.0

else 

    Rsto_PEt = 41000.0 / Gsto_PEt

end if



! =============================
! Estimate soil water potential
! =============================

! =============================
! Calculate P input
! =============================

if (precip == 0) then

precip=0

else if (precip >= 0) then

precip = (precip  / 1000.0)    ! Converts input precip in mm to m

end if

! For daily precipitation use, "_use" term

   hour_count  = hour_count + 1

   if (hour_count < 25) then

   precip_dd  = precip_dd + precip

   else if (hour_count == 25) then

      precip_use = precip_dd
      precip_dd = 0 + precip
      hour_count = 1

   end if
 

if (precip_use > 0) then

P_input = (Precip_use-(0.0001*LAI)) + ((LAI*0.0001)- (min(Ei_use, (0.0001*LAI))))

else

P_input = 0

end if

if (P_input < 0) then

P_input = 0

else

P_input = P_input

end if


P_input_meas = P_input

P_input_D1 = P_input


if ((P_input - SMD_D1) < 0) then

P_input_D2 = 0

else

P_input_D2 = P_input - SMD_D1

end if

if ((P_input - (SMD_D1 + SMD_D2)) < 0) then

P_input_D3 = 0

else

P_input_D3 = P_input - (SMD_D1 + SMD_D2)

end if


if ((P_input - (SMD_D1 + SMD_D2 + SMD_D3)) < 0) then

P_input_D4 = 0

else

P_input_D4 = P_input - (SMD_D1 + SMD_D2 + SMD_D3)

end if



Rinc = Rinc_b * SAI * h/ustar

! ======================
! Penman Monteith method
! ======================

esat = 611 * EXP((17.27*Ts_c)/(Ts_c+237.3))

eact = esat - (VPD * 1000)                    ! VPD in kPa

Tvir = (Ts_c+273.16)/(1-(0.378*(eact/P_atm)))  

delta= ((4098*esat)/((Ts_c+237.3)**2)) 

lamda = (2501000-(2361*Ts_c)) 

psychro = 1628.6 * (P_atm/lamda)

Pair = (0.003486*(P_atm/Tvir))

Cair = (0.622*((lamda*psychro)/P_atm)) 

G_J = Rn_J*0.1

! Save previous hour's Et_hr for LWP caluclations

ET_hr_1 = Et_hr


! EI, AEt, PEt calculations don't need to include Ra as VPD provided at 2 m
! above surface. Canopy Rb does need to be included

! =====================


ET_1 = ((Delta)*(Rn_J - G_J))/(lamda)

ET_2 = 3600* Pair * Cair * (VPD * 1000) / (RbH2O) / lamda

PET_3 = delta + psychro * (1.0+(Rsto_PEt*0.61)/RbH2O)       ! Assume Ra = 0

PEt_hr = ((ET_1 + ET_2) / PET_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method

ET_3 = delta + psychro * (1.0 + (Rsto_c * 0.61)/RbH2O)           ! Assume Ra = 0

Et_hr = ((ET_1 + ET_2) / ET_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                    ! give in m/day for comparison with old method



! =====================

! calculate delta_Et for LWP calculations

delta_Et = Et_hr_1 - ET_hr


!==========================
!soil evaporation Es
!==============================


t = exp(-0.5*LAI)                          !fraction of energy available at soil suraface
Rn_J_g = Rn_J*t                                 !energy available at soil surface
!Es_G_J = 0.1 * Rn_J_g


Es_1 = (Delta*(Rn_J_g))/(lamda)

Es_2 = 3600 * Pair * Cair * (VPD * 1000) / (Ra_u + RbH2O) / lamda

Es_3 = delta + psychro                          ! for evaporation from a surface the penman equation uses  heat condutance / water conductance (gh/gw). There is no surface resistance to water loss so this can be simplified to gH ~= gw e.g. gH/gw = 1


if (LAI > 1) then

Es_hr = 0

else if (Sn < Fc_m) then

Es_hr = 0


else

Es_hr = ((Es_1 + Es_2) / Es_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method
end if

Es_hr = 0

!==========================
!Calulate AET from Et and Es (after Shuttleworth and Wallace, 1985)
!==============================




SW_a = (delta + psychro) * (Ra_u + RbH2O)
SW_s = (delta + psychro) * Rinc + (psychro * 0)   !Rsoil for water at soil surface is assumed to be zero
SW_c = (delta + psychro) * 0 +(psychro * Rsto_c)   ! J-P says boundary layer resistance should be zero here

C_canopy =  1 / (1 + ((SW_c * SW_a) / (SW_s* (SW_c + SW_a))))
C_soil =    1 / (1 + ((SW_s * SW_a)/ (SW_c* (SW_s + SW_a))))


if (Es_hr == 0) then

AEt_hr = Et_hr

else

AEt_hr = (C_canopy * Et_hr) + (C_soil * Es_hr)

end if





!new penman method for estimating Ei

Ei_1 = ((Delta)*(Rn_J-G_J))/(lamda)

Ei_2 = 3600* Pair * Cair * (VPD * 1000) / RbH2O / lamda

Ei_3 = delta + psychro                          ! for evaporation from a surface the penman equation uses  heat condutance / water conductance (gh/gw). There is no surface resistance to water loss so this can be simplified to gH ~= gw e.g. gH/gw = 1

Ei_hr = ((Ei_1 + Ei_2) / Ei_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method




! For daily Ei and AEt_use, "_use" term

   hour_count_1  = hour_count_1 + 1

      if (hour_count_1 < 25) then

        Ei_dd  = Ei_dd + Ei_hr

        else if (hour_count_1 == 25) then

        Ei_use = Ei_dd
        Ei_dd = 0 + Ei_hr

        hour_count_1 = 1

      end if


   hour_count_2  = hour_count_2 + 1

     if (hour_count_2 < 25) then

      AEt_dd  = AEt_dd + AEt_hr
      !PET_dd = PEt_dd + PEt_hr
      !AET_dd = AEt_dd + AEt_hr
      Es_dd = Es_dd + Es_hr

      else if (hour_count_2 == 25) then

      AEt_use = AEt_dd
      AEt_dd = 0 + AEt_hr
 
    
      Es_use = Es_dd
      Es_dd = 0 + Es_hr

      hour_count_2 = 1

    end if


   hour_count_5  = hour_count_5 + 1

     if (hour_count_5 < 25) then

      PEt_dd  = PEt_dd + PEt_hr

      else if (hour_count_5 == 25) then

      PEt_use = PEt_dd
      PEt_dd = 0 + PEt_hr

 
      hour_count_5 = 1

    end if


 hour_count_3  = hour_count_3 + 1

   if (hour_count_3 < 25) then
     
     trans_diff = trans_diff
     Sn_diff = Sn_diff


     else if (hour_count_3 == 25) then
 
     trans_diff = P_input - (AEt_use+Es_use) 
     Sn_diff = (trans_diff/root)                          ! Uses Penman Monteith method                        
     hour_count_3 = 1


hour_count_3 = 1

   end if


 hour_count_4 = hour_count_4 + 1

 if (hour_count_4 < 25) then

   Sn = Sn
   SMD = SMD
!   WC = WC
   Per_vol = Per_vol
   SWP = SWP

 else if (hour_count_4 == 25) then

  Sn = min(Sn_star, Sn + Sn_diff)

if (Sn < PWP_vol) then
   Sn = PWP_vol
end if

  
!  WD = Sn_star - Sn_1
!  WC = Fc_m - WD
  Per_vol = Sn * 100
  ASW = (Sn - PWP_vol) * root
  SWP = SWP_AE*((SWC_sat/Sn)**soil_B)

if (SWP < -4) then
   SWP = -4

end if

! Save today's SWP for next day's LWP calculation

!SWP_1 = SWP_effec
SWP_1 = SWP

  SMD = (sn_star - sn) * root
  hour_count_4 = 1

 end if

 hour_count_6 = Hour_count_6 + 1

 if (hour_count_6 < 25) then

et_D1 = et_D1
et_D2 = et_D2
et_D3 = et_D3
et_D4 = et_D4
et_meas = et_meas

Et_D1_o = Et_D1_o
Et_D2_o = Et_D2_o
Et_D3_o = Et_D3_o
Et_D4_o = Et_D4_o

Trans_diff_D1 = Trans_diff_D1
Trans_diff_D2 = Trans_diff_D2
Trans_diff_D3 = Trans_diff_D3
Trans_diff_D4 = Trans_diff_D4
Trans_diff_meas = Trans_diff_meas

Sn_diff_D1 = Sn_diff_D1
Sn_diff_D2 = Sn_diff_D2
Sn_diff_D3 = Sn_diff_D3
Sn_diff_D4 = Sn_diff_D4
Sn_diff_meas = Sn_diff_meas

Sn_D1 = Sn_D1
Sn_D2 = Sn_D2
Sn_D3 = Sn_D3
Sn_D4 = Sn_D4
Sn_meas = Sn_meas

SWP_D1 = SWP_D1
SWP_D2 = SWP_D2
SWP_D3 = SWP_D3
SWP_D4 = SWP_D4
SWP_meas = SWP_meas

SMD_D1 = SMD_D1
SMD_D2 = SMD_D2 
SMD_D3 = SMD_D3 
SMD_D4 = SMD_D4 
SMD_meas = SMD_meas

fSWP_D1 = fSWP_D1
fSWP_D2 = fSWP_D2
fSWP_D3 = fSWP_D3
fSWP_D4 = fSWP_D4



 else if (hour_count_6 == 25) then


!transpiration at each depth

Et_D1 = AEt_use * R_D1

if (Et_D1 > ((Sn_D1-PWP_vol) * L1)) then

Et_D1_o = Et_D1 - ((Sn_D1-PWP_vol) * L1)
Et_D1 = (Sn_D1-PWP_vol) * L1


else

Et_D1_o = 0
Et_D1 = Et_D1

end if

Et_D2 = (AEt_use * R_D2) + Et_D1_o

if (Et_D2 > ((Sn_D2-PWP_vol) * L2)) then

Et_D2_o = Et_D2 - ((Sn_D2-PWP_vol) * L2)
Et_D2 = (Sn_D2-PWP_vol) * L2


else

Et_D2_o = 0
Et_D2 = Et_D2

end if


Et_D3 = (AEt_use * R_D3) + Et_D2_o

if (Et_D3 > ((Sn_D3-PWP_vol) * L3)) then

Et_D3_o = Et_D3 - ((Sn_D3-PWP_vol) * L3)
Et_D3 = (Sn_D3-PWP_vol) * L3


else

Et_D3_o = 0
Et_D3 = Et_D3

end if

Et_D4 = (AEt_use * R_D4) + Et_D3_o

if (Et_D4 > ((Sn_D4-PWP_vol) * L4)) then

Et_D4_o = Et_D4 - ((Sn_D4-PWP_vol) * L4)
Et_D4 = (Sn_D4-PWP_vol) * L4


else

Et_D4_o = 0
Et_D4 = Et_D4

end if


Et_meas = AEt_use * R_meas

if (Et_meas > ((Sn_meas-PWP_vol) * D_meas)) then

Et_meas = (Sn_meas-PWP_vol) * D_meas


else

Et_meas = Et_meas

end if




! change in soil water storage at each depth


trans_diff_D1 = P_input_D1 - et_D1
Sn_diff_D1 = (trans_diff_D1) / L1
Sn_D1 = min(FC_m, Sn_D1 + Sn_diff_D1)
if (Sn_D1 < PWP_vol) then
   Sn_D1 = PWP_vol
end if

trans_diff_D2 = P_input_D2 - et_D2
Sn_diff_D2 = ((trans_diff_D2)) / L2
Sn_D2 = min(FC_m, Sn_D2 + Sn_diff_D2)
if (Sn_D2 < PWP_vol) then
   Sn_D2 = PWP_vol
end if

trans_diff_D3 = P_input_D3 - et_D3
Sn_diff_D3 = ((trans_diff_D3)) / L3
Sn_D3 = min(FC_m, Sn_D3 + Sn_diff_D3)
if (Sn_D3 < PWP_vol) then
   Sn_D3 = PWP_vol
end if

trans_diff_D4 = P_input_D4 - et_D4
Sn_diff_D4 = ((trans_diff_D4)) / L4
Sn_D4 = min(FC_m, Sn_D4 + Sn_diff_D4)
if (Sn_D4 < PWP_vol) then
   Sn_D4 = PWP_vol
end if


trans_diff_meas = P_input_meas - et_meas
Sn_diff_meas = (trans_diff_meas) / D_meas
Sn_meas = min(FC_m, Sn_meas + Sn_diff_meas)
if (Sn_meas < PWP_vol) then
   Sn_meas = PWP_vol
end if

!Soil water potential at each depth

SWP_D1 = SWP_AE * ((SWC_sat / Sn_D1)**soil_b)
if (SWP_D1 < -4) then
   SWP_D1 = -4
end if

SWP_D2 = SWP_AE * ((SWC_sat / Sn_D2)**soil_b)
if (SWP_D2 < -4) then
   SWP_D2 = -4
end if

SWP_D3 = SWP_AE * ((SWC_sat / Sn_D3)**soil_b)
if (SWP_D3 < -4) then
   SWP_D3 = -4
end if

SWP_D4 = SWP_AE * ((SWC_sat / Sn_D4)**soil_b)
if (SWP_D4 < -4) then
   SWP_D4= -4
end if

SWP_meas = SWP_AE * ((SWC_sat / Sn_meas)**soil_b)
if (SWP_meas < -4) then
   SWP_meas = -4
end if


SWP_Effec = ((SWP_D1*r_D1)+(SWP_D2*r_D2)+(SWP_D3*r_D3)+(SWP_D4*r_D4))/ (r_D1 + r_D2 + r_D3 + r_D3)

!SMD at each depth

SMD_D1 = (Fc_m - Sn_D1) * L1
SMD_D2 = (Fc_m - Sn_D2) * L2
SMD_D3 = (Fc_m - Sn_D3) * L3
SMD_D4 = (Fc_m - Sn_D4) * L4

SMD_meas = (Fc_m - Sn_meas) * D_meas

hour_count_6 = 1
end if

!calculate fSWp at depth D


fSWP_D1 = (((-1) * SWP_D1)** (-0.706)) * 0.355
fsWP_D1 = max(fswp_D1, fmin)
if (fSWP_D1 > 1) then
   fSWP_D1 = 1
end if

fSWP_D2 = (((-1) * SWP_D2)**(-0.706)) * 0.355
fsWP_D2 = max(fswp_D2, fmin)
if (fSWP_D2 > 1) then
   fSWP_D2 = 1
end if

fSWP_D3 = (((-1) * SWP_D3)** (-0.706)) * 0.355
fsWP_D3 = max(fswp_D3, fmin)
if (fSWP_D3 > 1) then
   fSWP_D3 = 1
end if

fSWP_D4 = (((-1) * SWP_D4)** (-0.706)) * 0.355
fsWP_D4 = max(fswp_D4, fmin)
if (fSWP_D4 > 1) then
   fSWP_D4 = 1
end if




!total_e_Dk = (r_D1*fSWP_D1)+(r_D2*fSWP_D2)

! calculate total Sn_diff based on total extraction from all soil layers

trans_diff_layers = trans_diff_D1 + trans_diff_D2 + trans_diff_D3 + trans_diff_D4
Sn_diff_layers = trans_diff_layers / root






! ==============================================
! Calculate f for next days Gsto calculations
! ==============================================

! fswp=1/(0.75+(SWP/(-0.25))**1.5)   ! sloped fSWP relationship better fit to wheat data
                                 ! (used to parameterise model)

! If using default DO3SE model use:

fswp = (((-1) * SWP)** (-0.706)) * 0.355
!fswp = (1-fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin

fsWP = max(fswp, fmin)




if (fswp > 1) then
fswp = 1
end if

fswp_effec = (fswp_D1 + fswp_D2 + fswp_D3 + fswp_D4) / 4

if (fswp_effec > 1) then
fswp_effec = 1
end if


  ! LWP


!delta_t = 1



!If (hr < 3) then

!LWP_1 = SWP

!else

!LWP_1 = LWP

!end if

!if (hr < 3) then

!DeltaLWP = 0

!else

!DeltaLWP = ((((SWP-LWP_1-(Rsr+Rp)*(Et_hr_1*1000))/(C*(Rsr+Rp+Rc)))*Delta_t)-(((Rsr+Rp)*Rc)/(Rsr+Rp+Rc))*(delta_Et*1000))

!end if



!if (hr < 3) then

!LWP = SWP

!else

!LWP = LWP_1 + DeltaLWP

!end if


delta_t = 0
deltaLWP = 0
LWP_1 = 0


LWP = (((Aet_hr*1000)*(Rp+Rsr))-SWP) * (-1)

flwp = (((-1) * LWP)** (-0.706)) * 0.355
!flwp = (1-fmin) / (SWP_min - SWP_max) * (SWP_min - LWP) + fmin


flwp = max (flwp, fmin)


if (flwp > 1) then
flwp = 1
end if


! set fSWP to 1 for generic Med evergreen 

! fswp = 1

! ================================
! calculate ozone deposition terms
! ================================


! Rsur =              1
!       ---------------------------
!       LAI  +  LAI  +      1
!       ---     ---    ------------
!       Rsto    Rext   Rinc + Rgs


if (LAI > 0) then

Rsur = 1 / ((LAI/Rsto) + (SAI/Rext) + (1/(Rinc + Rgs)))

else if (SAI > 0) then

Rsur = 1 / ((SAI/Rext) + (1/(Rinc + Rgs)))

else if (SAI == 0) then

Rsur = 1 / (1/Rgs)


end if


! =========================================================
! Estimate canopy level O3 concentraion in nmol/m3
! =========================================================

! Make sure calculation works even if uzR below d+zo

if (czR < d+zo) then 

Ra_O3 = 1/(k*ustar)*(log(((zo+d)-d)/(h-d)))

else if (czR >= d + zo) then

Ra_O3 = 1/(k*ustar)*(log((czR-d)/(h-d)))

end if


! ===============================
! Estimate deposition velocity
! ===============================


Vd = (1/(Ra_O3 + Rb + Rsur))     ! in m/s


O3_ppb = O3_ppb_zR * (1-(Ra_O3 * (Vd)))       ! Estimates ozone concentration at 
                                              ! canopy height in (ppb)

O3_nmol_m3 = O3_ppb * 41.67   ! Estimates ozone concentration at canopy height 
                              ! in nmol/m3; N.B> need to do proper conversion
                              ! to include changes in T and P but no P in flux tower data......


! =================================================
! Estimate total ozone flux (nmol O3 m-2 PLA s-1)
! =================================================




Ftot = O3_nmol_m3 * Vd          ! in nmol O3 m-2 PLA s-1



! =========================================================
! Calculate ozone effects parameters (e.g. AFstY and AOT40)
! =========================================================


! Need to estimate upper canopy leaf gO3
! May want to use leaf_fphen.....


leaf_fphen = fphen       ! need to change to calculate fphen for
                         ! upper canopy leaf

gO3 = gmax * leaf_fphen * leaf_flight * ftemp * fVPD * fSWP   ! in mmol O3 m-2 s-1


 leaf_rb = 1.3 * 150 * sqrt(Lm/uh)    ! leaf boundary layer resistance in s/m
 leaf_gb = 1/leaf_rb                  ! leaf boundary layer conductance in m/s
 leaf_gb = leaf_gb

 if (Gsto_1 > 0) then

      leaf_r = 1.0/((1.0/Rsto_1) + (1.0/Rext)) ! leaf resistance in s/m

        if (leaf_fphen == 0) then

        Fst = Fst

        else if (leaf_fphen > 0) then

        Fst = O3_nmol_m3 * (1/Rsto_1) * (leaf_r/(leaf_rb + leaf_r))  ! Fst in nmol/m2/s

        end if

else 

Fst = 0

end if


! ================
! calculate AFstY
! ================

if (Fst <= Y) then

AFstY = AFstY

else if (Fst > Y) then

AFstY = AFstY + (((Fst-Y)*60*60)/1000000)  ! Cumulative Fst above Y in mmol/m2

end if

! =================================
! calculate AOT40 over Fphen period
! =================================

if (O3_ppb > 40) then

  OT40 = (O3_ppb - 40) / 1000

else
            OT40 = 0
        end if

        if ( PAR < 105.0 .or. fphen == 0 ) then  ! 50 W m-2 Global Radiation = PAR 105 (micromol m-2 s-1)
            OT40 = 0
        end if

        AOT40 = (AOT40 + OT40)


! =====================
! write output to file
! =====================

!write (unit=8, fmt=*) '"mm"', '"mdd"', '"dd"', '"hr"', '"SWP"', '"LWP"', &
!                      '"fLWP"', '"Sn"', '"P_input"', '"Gsto"'
write (unit=8, fmt=*) mm, mdd, dd, hr, SWP, LWP, fLWP, Sn, P_input, Gsto

end do

close(unit=9)
close(unit=8)

end program DOSE
