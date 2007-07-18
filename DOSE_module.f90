        module DOSE_module
            
            ! Input data composite type - read an entire line into a 
            ! variable of this type
            type, public :: input_record
                integer :: mm      ! month
                integer :: mdd     ! day of month
                integer :: dd      ! day of year
                integer :: hr      ! hour of day
                real :: Ts_c       ! surface air temperature in oC
                real :: VPD        ! Vapour pressure deficit (kPa)
                real :: precip     ! Precipitation (mm)
                real :: uh         ! Windspeed at top of canopy (m/s)
                real :: O3_ppb_zR  ! Ozone concentration at observation height (ppb)
                real :: Idrctt     ! Direct radiation in W/m2
                real :: Idfuse     ! Diffuse radiation in W/m2
                real :: zen        ! Zenith angle in degrees
            end type input_record

            ! Output data composite type - duplicates removed!
            type, public :: output_record
                integer :: mm, mdd, dd, hr
!                real :: Ra_O3, Rb, Rsto, Uzh, LAI, SAI, Fphen, Ts_c, &
!                        VPD, precip, precip_use, SMD, SWP, fswp, Gsto, &
!                        Rsur, Vd, Fst, AFstY, gO3, uh, O3_ppb, &
!                        PET_use, AET_use, Rsto_PEt, Ei_use, LAI, &
!                        ustar, Ra_O3, Sn_1, Sn, Ftot, Ra_u, Per_vol, ASW
                real :: Ra_O3, Rb, Rsto, Uzh, LAI, SAI, Fphen, Ts_c, &
                        VPD, precip, precip_use, SMD, SWP, fswp, Gsto, &
                        Rsur, Vd, Fst, AFstY, gO3, uh, O3_ppb, &
                        PET_use, AET_use, Rsto_PEt, Ei_use, &
                        ustar, Sn_1, Sn, Ftot, Ra_u, Per_vol, ASW
            end type output_record

            ! {{{
                ! =========================================
                ! Imported local variables, i.e. input data
                ! =========================================

                integer, public :: mm      ! month
                integer, public :: mdd     ! day of month
                integer, public :: dd      ! day of year
                integer, public :: hr      ! hour of day
                real, public :: Ts_c       ! surface air temperature in oC
                real, public :: ustar      ! Friction velocity (m/s)
                real, public :: VPD        ! Vapour pressure deficit (kPa)
                real, public :: precip     ! Precipitation (mm)
                real, public :: uh         ! Windspeed at top of canopy (m/s)
                real, public :: O3_nmol_m3 ! Canopy ozone concentration (nmol/m3)
                real, public :: Idfuse     ! Diffuse radiation in W/m2
                real, public :: Idrctt     ! Direct radiation in W/m2
                real, public :: O3_ppb_zR  ! Ozone concentration at observation height (ppb)
                real, public :: O3_ppb     ! canopy height O3 in ppb (for AOT40 calculation)
                real, public :: zen        ! Zenith angle in degrees
                real, public :: LAI        ! Grassland growth models LAI


                ! ====================================================
                ! Physical constants required for Ra & Rb calculations
                ! ====================================================

                ! von Karmans constant (k) = 0.41
                ! specific heat of air at constant pressure for dry air (cp, J/Kg/K) = 1005
                ! gravitational acceleration (g, m/s) = 9.8
                ! height of zref, 50m in EMEP model(O3z, m) = 50
                ! kinetic viscosity of air (v, m2/s at 20oC) = 0.000015
                ! molecular diffusivity of O3 in air relative, &
                !                                 to water vapour (DO3, m2/s) = 0.000015
                ! Prandtl Number (Pr, -) = 0.72

                real, parameter, public :: k=0.41

                integer, parameter, public :: cp=1005
                real, parameter, public :: g=9.8
                real, parameter, public :: czR=25      ! Reference height for O3 concentration
                real, parameter, public :: uzR=25      ! Reference height for wind speed

                real, parameter, public :: v=0.000015
                real, parameter, public :: DO3=0.000015
                real, parameter, public :: Pr=0.72
                real, parameter, public :: h=25             ! Canopy height
                real, parameter, public :: zo=h*0.1         ! roughness length (h*0.1)
                real, parameter, public :: d=h*0.7          ! displacement height (h*0.7)


                ! ============================
                ! Calculated Ra & Rb variables
                ! ============================


                real, public :: Ra_u         ! Atmospheric resistance for windspeed calculations (s/m)
                                     ! Also used in SMD calcs. as assumed met variables
                                     ! will be measured at same height (e.g. VPD and wind speed)
                real, public :: Ra_O3        ! Atmospheric resistance for ozone calculations (s/m)
                real, public :: uzh          ! Wind speed at top of canopy (i.e. h) (m/s)
                                     ! N.B. Windseepd goes to zero at (d + zo) 
                real, public :: Rb           ! Quasi-laminar boundary layer resistance (s/m)


                ! =========================
                ! SMD calculation variables
                ! =========================

                real, public :: Ei_hr      ! Hourly intercepted evaporation
                real, public :: AEt_hr     ! Hourly actual transpiration
                real, public :: PEt_hr     ! Hourly potential transpiration
                real, public :: PWP        ! Calculated PWP in m3/3
                real, public :: ASW        ! Calculated ASW in m3/m3
                real, public :: Sn_star    ! Calculated Sn* in m3/m3
                real, public :: Sn         ! soil Water storage capacity
                real, public :: Sn_1       ! soil water storage capacity of previous day
                real, public :: per_vol    ! % volumetric water content
                real, public :: SMD        ! soil moisture deficit in mm
                real, public :: SWP        ! Soil water potential in MPa
                real, public :: WC         ! water content
                real, public :: precip_dd  ! cumulated daily precipitation
                real, public :: precip_use ! daily precipitation used in calculations
                real, public :: Ei_dd      ! cumulated daily intercepted evaporation
                real, public :: Ei_use     ! daily intercepted evaporation used in calculations
                real, public :: AEt_dd     ! cumulated daily actual transpiraton
                real, public :: AEt_use    ! daily transpiration used in calculations
                real, public :: PEt_dd     ! cumulated daily potential transpiraton
                real, public :: PEt_use    ! daily potential used in calculations
                real, public :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations

                integer, public :: hour_count, hour_count_1, hour_count_2, hour_count_3, &
                           hour_count_4, hour_count_5

                ! =====================
                ! Rsur & go3 parameters
                ! =====================

                real, parameter, public :: SGS = 121            ! start of bulk canopy growth period
                real, parameter, public :: EGS = 273          ! end of bulk canopy growth period
                real, parameter, public :: Astart = 121         ! start of upper leaf growth period
                real, parameter, public :: Aend = 273         ! end of upper leaf growth period

                real, parameter, public :: LAI_max = 4.0        ! maximum LAI in m2/m2 
                real, parameter, public :: LAI_min = 0      ! minimum LAI in m2/m2 
                real, parameter, public :: Ls = 30            ! days to go from min LAI in m2/m2 to max 
                real, parameter, public :: Le = 30            ! days to go from max LAI in m2/m2 to min 


                real, parameter, public :: gmax = 148         ! mmol O3 m-2 PLA s-1
                real, parameter, public :: fmin = 0.13         ! minimum gs

                real, parameter, public :: fphen_a = 0      ! fphen at SGS
                real, parameter, public :: fphen_b = 0      ! fphen at Astart
                real, parameter, public :: fphen_c = 1.0      ! fphen midway during season
                real, parameter, public :: fphen_d = 0      ! fphen at Aend and EGS
                real, parameter, public :: fphenS  = 15       ! period to fphen_c
                real, parameter, public :: fphenE  = 20       ! period to fphen_d 


                real, parameter, public ::  PI = 3.14159265358979312     ! pi
                real, parameter, public ::  DEG2RAD = PI/180.0           ! Degrees -> Radians
                real, parameter, public ::  nydays = 365                 ! no. days per year (365 or 366)
                real, parameter, public ::  cosA    = 0.5                ! A = mean leaf inclination (60 deg.)
                                                                 ! where it is assumed that leaf
                                                   ! inclination has a spherical distribution

                real, parameter, public :: albedo = 0.12                  ! 0.2 is value for crops, 
                                                 ! 0.12 for needle leaf trees, 
                                                 ! 0.16 for broad leaf trees
                                                                 ! 0.14 for moorland
                real, parameter, public :: PARfrac = 0.45                ! approximation to fraction (0.45
                                                   ! to 0.5) of total
                                                                 ! radiation in PAR waveband (400-700nm)
                real, parameter, public :: Wm2_uE  = 4.57                ! converts from W/m^2 to umol/m^2/s
                real, parameter, public :: Wm2_2uEPAR= PARfrac * Wm2_uE  ! converts from W/m^2 to umol/m^2/s PAR
                real, parameter, public :: f_lightfac = 0.006             ! single leaf flight co-efficient

                real, parameter, public ::  T_min = 0        ! oC min temperature for g
                real, parameter, public ::  T_opt = 21         ! oC opt temperature for g
                real, parameter, public ::  T_max = 35        ! oC max temperature for g

                real, parameter, public :: VPD_max = 1.0      ! VPD for max g
                real, parameter, public :: VPD_min = 3.25      ! VPD for min g

                ! fswp = 1 for generic Med evergreen (use dummy values here and set fSWP = 1 later)
                real, parameter, public :: SWP_max = -0.05    ! SWP for max g
                real, parameter, public :: SWP_min = -1.25    ! SWP for min g

                real, parameter, public :: seaP = 101.325     ! sea level presuure in kPa
                real, parameter, public :: Rsoil = 200        ! Soil resistance in s/m
                real, parameter, public :: Rinc_b = 14        ! Rinc co-efficient
                real, parameter, public :: Rext = 2500        ! external plant cuticle resistance in s/m
                real, parameter, public :: Ts_k = 273.15      ! Conversion from ToC to T Kelvin

                ! ********************************************************************
                ! Soil water release curve constants; after Millthorpe & Moorby, 1974)
                ! ********************************************************************

                real, parameter, public :: soil_BD = 1.3    ! Soil bulk density (g/cm^3)
                                                    ! coarse = 1.6, medium = 1.3, fine = 1.1
                real, parameter, public :: soil_a = -5.5    ! SWC constant a
                                                    ! coarse = -4, medium = -5.5, fine = -7
                real, parameter, public :: soil_b = -3.3    ! SWC constant b
                                                    ! coarse = -2.3, medium -3.3, fine = -5.4
                real, parameter, public :: Fc_m = 0.193      ! Field capacity(m3/m3)
                                                    ! coarse = 0.15, medium = 0.27, fine = 0.43
                real, parameter, public :: root = 1.2         ! root depth, soil and species specific (m)

                real, parameter, public :: Lm = 0.05       ! Leaf dimension (m)
                real, parameter, public :: Y = 1.6           ! Threshold (Y) in AFstY, nmol O3 m-2 s-1


                ! =============================================
                ! Calculated deposition, Rsur and go3 variables
                ! =============================================

                real, public :: SAI              ! Stand Area Indea m2/m2

                real, public :: Gsto             ! Bulk stomatal conductance mmol O3 m-2 PLA s-1
                real, public :: Gsto_PEt         ! Bulk stomatal conductance mmol O3 m-2 PLA s-1
                                 ! assuming no soil water limit
                real, public :: Gsto_sm          ! Bulk stomatal conductance s/m
                real, public :: gO3              ! Upper leaf stomatal conductnce mmol O3 m-2 PLA s-1
                real, public :: leaf_gO3         ! Upper leaf stomatal condctance m/s
                real, public :: leaf_rO3         ! Upper leaf stoamtal resistance s/m
                real, public :: leaf_r           ! leaf resistance s/m

                real, public :: fphen            ! phenology related bulk g
                real, public :: flight           ! Canopy average gsto in relation to canopy light
                real, public :: ftemp            ! temperate related g
                real, public :: bt               ! ftemp variable
                real, public :: fVPD             ! VPD related g
                real, public :: Rsto             ! average canopy leaf stomatal resistance to O3 in s/m
                real, public :: fSWP             ! SWP related g
                real, public :: Rinc             ! In-canopy aerodynamic reistance
                real, public :: Rsur             ! Surface resistance to ozone in s/m
                real, public :: Ftot             ! Total ozone flux to vegetated surface in nmol O3 m-2 PLA s-1

                real, public :: leaf_fphen       ! phenology related to leaf g
                real, public :: leaf_flight      ! light related g
                real, public :: leaf_rb          ! leaf level rb in s/m
                real, public :: leaf_gb          ! leaf level gb in m/s


                ! flight variables

                real, public :: PARsun
                real, public :: PARshade
                real, public :: LAIsunfrac
                real, public :: sinB            ! B = solar elevation angle complement
                                        ! of zenith angle
                real, public :: sunLAI          ! sunlit LAI
                real, public :: f_shade         ! shade-leaf contribution to f_light

                real, public :: Rlow            ! Low temperature resistance(af.Wesely, 1989)
                real, public :: Rgs             ! Non vegetative surface resistance
                                ! including low temperature and snow


                real, public :: Vd     		! Deposition velocity of ozone (m/s)
                real, public :: Fst   		! Upper leaf stomatal ozone flux (nmol O3 m-2 PLA s-1)
                real, public :: AFstY 		! Accumulated stomatal flux above a threshold Y (mmol O3 m-2 PLA)
                real, public :: OT40   		! Ozone over 40 ppb over fphen period (ppm)
                real, public :: AOT40  		! AOT40 over bulk canopy growth period (ppm.hrs)
            ! }}}
            

            ! Make functions visible
            public :: run, init

        contains

            subroutine run(input, output)

                type(input_record), intent(in) :: input
                type(output_record), intent(out) :: output


                !--------------------------------------------------------------
                ! BEGIN ORIGINAL CALCULATION CODE
                !--------------------------------------------------------------
                ! {{{
                
                ! Calculates "canopy scale" Ra, Rb, Rsur and Vd and leaf AFstY using local EMEP
                ! met data

                ! Copy input variables
                mm          = input%mm
                mdd         = input%mdd
                dd          = input%dd
                hr          = input%hr
                Ts_c        = input%Ts_c
                VPD         = input%VPD
                precip      = input%precip
                uh          = input%uh
                O3_ppb_zR   = input%O3_ppb_zR
                Idrctt      = input%Idrctt
                Idfuse      = input%Idfuse
                zen         = input%zen

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

                ! ================
                ! Calculate Flight
                ! ================

                ! *****************************
                ! calculate PARsun and PARshade
                ! *****************************
                ! N.B. This part of the algorithm seems to produce the "floating underflow"


                if (zen <= 88 .and. LAI > 0) then

                ! N.B. Dave Simpson was using zen < 89.9 but this seemed to produce a
                ! floating underflow, if use < 88 the problem seems to be solved
                ! with no change to the results.

                   sinB = cos(zen*DEG2RAD)    ! uses EMEP output zen to estimate sinB
                                              ! ensures consistency between zen and &
                                              ! Idrctt & Idfuse


                   sunLAI = (1.0 - exp(-0.5*LAI/sinB) ) * sinB/cosA
                   LAIsunfrac = sunLAI/LAI

                    ! PAR flux densities evaluated using method of Norman (1982, p.79):
                    ! "conceptually, 0.07 represents a scattering coefficient"


                   PARshade = Idfuse * exp(-0.5*LAI**0.7) +  &
                               0.07 * Idrctt  * (1.1-0.1*LAI)*exp(-sinB)

                   PARsun = Idrctt *cosA/sinB + PARshade

                    ! .. Convert units, and to PAR fraction and multiply by albedo...

                  PARshade = PARshade * Wm2_2uEPAR * ( 1.0 - albedo )
                  PARsun   = PARsun   * Wm2_2uEPAR * ( 1.0 - albedo )

                else if (zen > 88 .or. LAI == 0 .or. Idrctt == 0) then

                  sinB = 0
                  LAIsunfrac = 0
                  PARshade = 0
                  PARsun = 0

                end if

                ! ********************************
                ! calculate Flight and leaf_flight
                ! ********************************

                leaf_flight   = (1.0 - exp (-f_lightfac*PARsun) )
                f_shade       = (1.0 - exp (-f_lightfac*PARshade) )

                Flight        = LAIsunfrac * leaf_flight + (1.0 - LAIsunfrac) * f_shade

                ! ================
                ! Calculate ftemp
                ! ================


                bt = (T_max-T_opt)/(T_opt-T_min)

                ftemp = ((Ts_c-T_min)/(T_opt-T_min))*((T_max-Ts_c)/(T_max-T_opt))**bt
                ftemp = max(ftemp, fmin)


                ! ===============
                ! Calculate fVPD
                ! ===============

                fVPD = ((1-fmin)*(VPD_min-VPD)/(VPD_min-VPD_max))+fmin
                fVPD = max(fVPD, fmin)

                if (fVPD > 1) then
                fvPD = 1
                end if

                ! =======================================
                ! Calculate Gsto using previous days fSWP
                ! =======================================


                Gsto = gmax * Fphen * Flight * ftemp * fVPD * fSWP   ! in mmol O3 m-2 s-1

                ! (using factor 41000 from mmol O3/m2/s to s/m given in Jones, App. 3
                !  for 20 deg.C )


                ! ===================================================================
                ! Calculate Gsto for PEt calculation (i.e. assuming non-limiting SWP)
                ! ===================================================================

                Gsto_PEt = gmax * Fphen * Flight * ftemp * fVPD 	! in mmol O3 m-2 s-1

                  if (Gsto_PEt == 0 .or. LAI == 0) then

                  Rsto_PEt = 100000         					! to allow for negligible Rsto

                  else if (Gsto_PEt > 0 .and. LAI > 0) then

                  Rsto_PEt = 1/((Gsto_PEt * LAI) / 41000)   		! potential bulk canopy stomatal
                                                    ! resistance to O3 in s/m

                  end if


                ! ===============================

                Gsto_sm = Gsto / 41000               ! in s/m for SWP calculation

                if (LAI == 0) then

                Gsto = 0

                else if (Gsto > 0) then

                Gsto = Gsto * LAI       ! estimates whole canopy stomatal conductance from
                                        ! average leaf in canopy stomatal conductance

                end if


                ! =============================
                ! Estimate soil water potential
                ! =============================


                if (precip == 0) then

                precip=0

                else if (precip >= 0) then

                precip = precip  / 1000    ! Converts input precip in mm to m

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


                   if (Gsto_sm <= 0) then

                     Rsto = 100000

                   else if (Gsto_sm > 0) then

                     Rsto = 1/(Gsto_sm)  		! Rsto for O3 in s/m

                   end if

                Rlow = 1000*exp(-(Ts_c+4))

                Rgs = Rsoil + Rlow + 2000*0
                Rgs = Rgs

                Rinc = Rinc_b * SAI * Rinc_b/ustar

                ! EI, AEt, PEt calculations don't need to include Ra as VPD provided at 2 m
                ! above surface. Canopy Rb does need to be included

                Ei_hr = ((vpd)*3600*18)/(seaP*((Rb*0.61)) * 0.0224 &
                              *((Ts_c+Ts_K) / Ts_K)*10**6)




                   if (LAI == 0 .or. SWP <= SWP_min) then

                     AEt_hr = 0

                     else if (LAI > 0 .or. SWP > SWP_min) then

                     AEt_hr = ((vpd)*3600*18)/(seaP*((Rb*0.61) &
                              +((Rsto*0.61)/LAI))*0.0224 &
                              *((Ts_c+Ts_K)/Ts_K)*10**6)

                   end if

                ! Calculation of potential evapotranspiration (PEt)

                ! ==========
                ! old method
                ! ==========

                   if (LAI == 0) then

                     PEt_hr = 0

                     else if (LAI > 0) then

                     PEt_hr = ((vpd)*3600*18)/(seaP*((Rb*0.61) &
                              +(((1/(Gsto_PEt/41000))*0.61)/LAI))*0.0224 &
                              *((Ts_c+Ts_K)/Ts_K)*10**6)

                   end if

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

                      else if (hour_count_2 == 25) then

                      AEt_use = AEt_dd
                      AEt_dd = 0 + AEt_hr

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

                     Sn = Sn


                     else if (hour_count_3 == 25 .and. Precip_use == 0) then
                 
                     Sn = -((AEt_use)/root)                               
                     hour_count_3 = 1

                     else if (hour_count_3 == 25 .and. Precip_use > 0) then

                  !allows at least 30% of P to recharge soil water directly

                     Sn = (Precip_use * 0.3) + ((Precip_use * 0.7) - (min(Ei_use, (precip_use * 0.7))) )/root 

                     hour_count_3 = 1

                   end if


                 hour_count_4 = hour_count_4 + 1

                 if (hour_count_4 < 25) then

                   Sn_1 = Sn_1
                   SMD = SMD
                   WC = WC
                   Per_vol = Per_vol
                   SWP = SWP

                 else if (hour_count_4 == 25) then

                  Sn_1 = min(Sn_star, Sn_1 + Sn)
                  SMD = (Sn_star - Sn_1)
                  WC = Fc_m - (SMD)
                  Per_vol = ((Fc_m - SMD) + PWP) * 100
                  ASW = Fc_m - SMD
                  SWP = (soil_a * 0.01) * ((WC/soil_BD))**soil_b/1000
                  hour_count_4 = 1

                 end if

                ! ==============================================
                ! Calculate fsWP for next days Gsto calculations
                ! ==============================================

                 fswp=1/(0.75+(SWP/(-0.25))**1.7)   ! sloped fSWP relationship better fit to wheat data
                                                 ! (used to parameterise model)

                ! If using default DO3SE model use:

                !fswp = (1-fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin
                !fsWP = max(fswp, fmin)

                if (fswp > 1) then
                fswp = 1
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
                !       Rsto    Rext   Rinc + Rsoil


                if (LAI > 0) then

                Rsur = 1 / ((LAI/Rsto) + (SAI/Rext) + (1/(Rinc + Rsoil)))

                else if (SAI > 0) then

                Rsur = 1 / ((SAI/Rext) + (1/(Rinc + Rsoil)))

                else if (SAI == 0) then

                Rsur = 1 / (1/Rsoil)


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

                 if (gO3 > 0) then

                     leaf_gO3 = gO3/41000             ! leaf stomatal conductance in m/s

                     leaf_rO3 = 1/leaf_gO3            ! leaf stomatal resistance in s/m
                     leaf_rO3 = leaf_rO3

                     leaf_r = 1/(leaf_gO3 + (1/2500)) ! leaf resistance in s/m

                        if (leaf_fphen == 0) then

                        Fst = Fst

                        else if (leaf_fphen > 0) then

                        Fst = O3_nmol_m3 * leaf_gO3 * (leaf_r/(leaf_rb + leaf_r))  ! Fst in nmol/m2/s

                        end if

                else if (gO3 == 0) then

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

                else if (O3_ppb <= 40) then

                  OT40 = 0

                end if

                if (Idfuse > 0) then

                  OT40 = OT40

                else if (Idfuse == 0) then

                  OT40 = 0

                end if

                if (Fphen > 0) then

                  OT40 = OT40

                else if (Fphen == 0) then

                 OT40 = 0

                end if

                AOT40 = (AOT40 + OT40)


                ! Copy output variables
                output%mm           = mm
                output%mdd          = mdd
                output%dd           = dd
                output%hr           = hr
                output%Ra_O3        = Ra_O3
                output%Rb           = Rb
                output%Rsto         = Rsto
                output%Uzh          = Uzh
                output%LAI          = LAI
                output%SAI          = SAI
                output%Fphen        = Fphen
                output%Ts_c         = Ts_c
                output%VPD          = VPD
                output%precip       = precip
                output%precip_use   = precip_use
                output%SMD          = SMD
                output%SWP          = SWP
                output%fswp         = fswp
                output%Gsto         = Gsto
                output%Rsur         = Rsur
                output%Vd           = Vd
                output%Fst          = Fst
                output%AFstY        = AFstY
                output%gO3          = gO3
                output%uh           = uh
                output%O3_ppb       = O3_ppb
                output%PET_use      = PET_use
                output%AET_use      = AET_use
                output%Rsto_PEt     = Rsto_PEt
                output%Ei_use       = Ei_use
                !output%LAI          = LAI
                output%ustar        = ustar
                !output%Ra_O3        = Ra_O3
                output%Sn_1         = Sn_1
                output%Sn           = Sn
                output%Ftot         = Ftot
                output%Ra_u         = Ra_u
                output%Per_vol      = Per_vol
                output%ASW          = ASW

                ! }}}
            
            end subroutine run

            subroutine init()

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
                   Ei_use            = 0
                   AEt_use           = 0
                   AEt_dd            = 0
                   PEt_use           = 0
                   PEt_dd            = 0
                   Ei_dd             = 0
                   SMD               = 0
                   WC                = 0
                   Sn                = 0

                ! *******************************

                ! ===============================
                ! Calculate Wstar for medium soil
                ! ===============================

                PWP = soil_BD*((SWP_min/(soil_a*(0.01)))*1000)**(1/soil_b)
                ASW = Fc_m - PWP
                Sn_star = ASW

                ! Initialize SWP variables, MPa (according to soil specific attributes)

                   SWP         = (soil_a*0.01)*((FC_m/soil_bd))**soil_b/1000
                   Sn_1        = Sn_star
                   WC          = Fc_m - PWP
                   Per_vol     = (Fc_m + PWP) * 100 
                   fSWP        = 1

                print *, Sn_star, SWP, Sn_1, WC


                ! Initialize other vaiables

                   AFstY      = 0
                   Fst        = 0
                   LAIsunfrac = 0
                   AOT40      = 0
                   OT40       = 0

            end subroutine init

        end module DOSE_module

