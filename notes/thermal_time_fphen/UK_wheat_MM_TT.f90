Program DOSE

! Calculates "canopy scale" Ra, Rb, Rsur and Vd and leaf AFstY using local EMEP
! met data

! =========================================
! Imported local variables, i.e. input data
! =========================================

integer :: mm      ! month
integer :: mdd     ! day of month
integer :: dd      ! day of year
integer :: hr      ! hour of day
integer :: emep_i, emep_j  ! emep grid co-ordinates
real :: lat        ! emep latitude centroid
real :: Ts_c       ! surface air temperature in oC
real :: ustar      ! Friction velocity (m/s)
real :: VPD        ! Vapour pressure deficit (kPa)
real :: psurf      ! surface air pressure (hPa)
real :: Hd         ! Sensible Heat (w/m2)
real :: precip     ! Precipitation (mm)s
real :: uh         ! Windspeed at top of canopy (m/s)
real :: Idfuse     ! Diffuse radiation in W/m2
real :: Idrctt     ! Direct radiation in W/m2
real :: O3_ppb_zR  ! Ozone concentration at observation height (ppb)
real :: Rn_J       ! Net radiation (J m-2 h-1)

real :: solar_dec  ! Solar declaration in degrees 
real :: dec        ! Solar declination variable
real :: hr_angle   ! Hour angle of the sun


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

real, parameter :: k=0.41
integer, parameter :: Rmass=287
integer, parameter :: cp=1005
real, parameter :: g=9.8
real, parameter :: R=8.31451   ! Universal gas constant JK-1 mol-1 or m3 Pa K-1mol-1
real, parameter :: z=50        ! Height at which EMEP model output provided


real, parameter :: v=0.000015
real, parameter :: DO3=0.000015
real, parameter :: Pr=0.72
real, parameter :: h=1             ! Canopy height

integer :: i, max_lines, ios

! ============================
! Calculated Ra & Rb variables
! ============================

real :: rho     ! surface density of dry air (Kg/m2)
real :: Tk      ! surface air temperature in K
real :: L       ! Monin-Obukov length
real :: zo      ! roughness length (h*0.1)
real :: d       ! displacement height (h*0.7)
real :: Ezd     ! stability function E(z-d)
real :: Ezo     ! stability function E(zo)
real :: Xzd     ! stability function X(z-d)
real :: Xzo     ! stability function X(zo)
real :: Psi_h_zd   ! 
real :: Psi_m_zd   ! 
real :: Psi_h_zo   ! 
real :: Psi_m_zo   ! 
real :: Ra         ! Atmospheric resistance (s/m)
real :: Rb         ! Quasi-laminar boundary layer resistance (m/s)
real :: O3_nmol_ch ! Canopy height ozone concentration in nmol/m3
real :: O3_ppb_ch     ! canopy height O3 in ppb (for AOT40 calculation)

! =========================
! SMD calculation variables
! =========================

real :: Ei_hr      ! Hourly intercepted evaporation
real :: AEt_hr     ! Hourly actual transpiration
real :: PEt_hr     ! Hourly potential transpiration
real :: ASW        ! Calculated ASW in m3/m3
real :: Sn_star    ! Calculated Sn* in m3/m3
real :: Sn         ! soil Water storage capacity
real :: Sn_1       ! soil water storage capacity of previous day
real :: per_vol    ! % volumetric water content
real :: SMD        ! soil moisture deficit in mm - total amount of water required to recharge root zone
real :: WD         ! water deficit m/m  - water deficit per meter of root zone
real :: SWP        ! Soil water potential in MPa
!real :: SWPcomp_a  ! SWP component A
!real :: SWPcomp_b  ! SWP component B
real :: WC         ! water content
real :: precip_dd  ! cumulated daily precipitation
real :: precip_use ! daily precipitation used in calculations
real :: Ei_dd      ! cumulated daily intercepted evaporation
real :: Ei_use     ! daily intercepted evaporation used in calculations
real :: AEt_dd     ! cumulated daily actual transpiraton
real :: AEt_use    ! daily transpiration used in calculations
real :: PEt_dd     ! cumulated daily potential transpiraton
real :: PEt_use    ! daily potential used in calculations
real :: Rsto_PEt   ! Rsto for H2O for use in SMD calculations
real :: SWP_min_vol ! SWP min converted from MPa to m3/m3




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
real :: AET_3      ! PM AEt calculation (in mm/day converted to m/day by 1000)
real :: PET_3      ! PM PEt calculation (in mm/day coverted to m/day by 1000)
real :: Ei_1       ! PM Ei calculation step 1
real :: Ei_2       ! PM Ei calculation step 2
real :: Ei_3       ! PM Ei calculation step 3
real :: PM_AEt_hr  ! PM (Penman Monteith AEt, mm/h)
real :: PM_AEt_dd  ! cumulated daily actual Penman-Monteith transpiraton, mm/day
real :: PM_AEt_use ! Penman Monteith daily transpiration used in calculations (mm/day)
real :: PM_PEt_hr  ! PM (Penman Monteith AEt, mm/h)
real :: PM_PEt_dd  ! cumulated daily actual Penman-Monteith transpiraton, mm/day
real :: PM_PEt_use ! Penman Monteith daily transpiration used in calculations (mm/day)


integer :: hour_count, hour_count_1, hour_count_2, hour_count_3, &
           hour_count_4, hour_count_5, hour_count_6, hour_count_7, &
           hour_count_8, hour_count_9, hour_count_10


!========================
! Use thermal time to estimate following variables
!========================

integer:: Mid_anthesis      ! latitude estimated mid-anthesis
integer:: SGS               ! start of bulk canopy growth period and period from which to accumulate TT
integer:: EGS               ! end of bulk canopy growth period

integer:: Astart            ! start of upper leaf growth period
integer:: Aend              ! end of upper leaf growth period


real :: T_dd                ! Accumulates daily ToC
real :: T_avg               ! Average daily ToC
real, parameter :: Tb=0     ! Baseline effective temperature ToC
real :: T_sum               ! Degree days


! =====================
! Rsur & go3 parameters
! =====================


real, parameter :: LAI_max = 3.5        ! maximum LAI in m2/m2
real, parameter :: LAI_min = 0        ! minimum LAI in m2/m2 
real, parameter :: Ls = 70            ! days to go from min LAI in m2/m2 to max 
real, parameter :: Le = 22            ! days to go from max LAI in m2/m2 to min 


real, parameter :: gmax = 500         ! mmol O3 m-2 PLA s-1
real, parameter :: fmin = 0.01         ! minimum gs

! Bulk Fphen......

real, parameter :: fphen_a = 1.0      ! fphen at SGS
real, parameter :: fphen_b = 1.0      ! fphen at Astart
real, parameter :: fphen_c = 1.0      ! fphen midway during season
real, parameter :: fphen_d = 0.1      ! fphen at Aend and EGS
real, parameter :: fphenS  = 0        ! period to fphen_c
real, parameter :: fphenE  = 45       ! period to fphen_d 

! Flag leaf fphen.....N.B. Not using this in this model as using thermal time

real, parameter :: leaf_fphen_a = 0.0      ! fphen at SGS
real, parameter :: leaf_fphen_b = 0.8      ! fphen at Astart
real, parameter :: leaf_fphen_c = 1.0      ! fphen midway during season
real, parameter :: leaf_fphen_d = 0.2      ! fphen at Aend and EGS
real, parameter :: leaf_fphenS  = 15        ! period to fphen_c
real, parameter :: leaf_fphenE  = 40       ! period to fphen_d


real, parameter ::  PI = 3.14159265358979312     ! pi
real, parameter ::  DEG2RAD = PI/180.0           ! Degrees -> Radians
real, parameter ::  nydays = 365                 ! no. days per year (365 or 366)
real, parameter ::  cosA    = 0.5                ! A = mean leaf inclination (60 deg.)
                                                 ! where it is assumed that leaf
  							       ! inclination has a spherical distribution

real, parameter :: albedo = 0.2                  ! 0.2 is value for crops, 
								 ! 0.12 for needle leaf trees, 
								 ! 0.16 for broad leaf trees
                                                 ! 0.14 for moorland
real, parameter :: PARfrac = 0.45                ! approximation to fraction (0.45
							       ! to 0.5) of total
                                                 ! radiation in PAR waveband (400-700nm)
real, parameter :: Wm2_uE  = 4.57                ! converts from W/m^2 to umol/m^2/s
real, parameter :: Wm2_2uEPAR= PARfrac * Wm2_uE  ! converts from W/m^2 to umol/m^2/s PAR
real, parameter :: f_lightfac = 0.0105             ! single leaf flight co-efficient

real, parameter ::  T_min = 12        ! oC min temperature for g
real, parameter ::  T_opt = 26         ! oC opt temperature for g
real, parameter ::  T_max = 40        ! oC max temperature for g

real, parameter :: VPD_max = 1.2      ! VPD for max g
real, parameter :: VPD_min = 3.2      ! VPD for min g
real, parameter :: VPDsum_crit = 8    ! Critical VPD sum value (wheat = 8 kPa, potato = 10 kPa)


! fswp = 1 for these runs
real, parameter :: SWP_max = -0.3    ! SWP for max g
real, parameter :: SWP_min = -1.1    ! SWP for min g
real, parameter :: PWP = -4          ! PWP (MPa) cut off - as threshold below which fswp - 0.01


real, parameter :: seaP = 101.325     ! sea level presuure in kPa
real, parameter :: Rsoil = 200        ! Soil resistance in s/m
real, parameter :: Rinc_b = 14        ! Rinc co-efficient
real, parameter :: Rext = 2500        ! external plant cuticle resistance in s/m
real, parameter :: Ts_k = 273.15      ! Conversion from ToC to T Kelvin


!==========================================
! Mesophylly model parameters and variables
!==========================================

real :: gmes       ! in mmol m-2 s-1
real :: gmes_ms    ! in m/s
real :: Rmes       ! in s/m
real :: gsto_mes   ! includes gsto and gmes in series to estimate stomatal uptake conductance  

real :: fmes_hr
real :: fmes_O3
real :: fmes_PAR
real :: fmes_temp
real :: bt_mes
real :: fmes_VPD
real :: leaf_r_mes   ! leaf resistance including mesophyll resistance in s/m 
real :: Fst_mes      ! ozone flux according to Rmes (nmol m-2 s-1)
real :: Detox        ! Detoxified Fst based on Rmes (i.e. Fst (no threshold) - Fst_mes) nmol m-2 s-1 
real :: AFstY_Rmes   ! AFst determined according to Rmes rather than fixed threshold Y

real, parameter :: gmes_max = 130          ! in mmol O3 m-2 s-1
real, parameter :: gmes_min = 70           ! in mmol O3 m-2 s-1

real, parameter ::  fmin_mes = 0.5
real, parameter ::  T_min_mes = 10         ! oC min temperature for g
real, parameter ::  T_opt_mes = 22         ! oC opt temperature for g
real, parameter ::  T_max_mes = 42         ! oC max temperature for g
real, parameter ::  VPD_max_mes = 2.2      ! VPD for max g
real, parameter ::  VPD_min_mes = 4.2      ! VPD for min g






! ********************************************************************
!Soil water release constants after Campbell (1985) with constants defined from
!experimental data by Tuzet et al (2003)

!***************************************************

real, parameter :: soil_BD = 1.6    ! Soil bulk density (g/cm^3)
                                    ! coarse = 1.6, medium = 1.3, fine = 1.1


real, parameter :: Fc_m = 0.16      ! Field capacity(m3/m3)
                                    ! coarse (sandy loam) = 0.14-0.19, medium (Loam) = 0.24-0.28, fine (silt loam) = 0.28-0.3
                                    !clay loam = 0.36-0.38
                                    ! Field capacities are set by SWP = -0.01 Mpa


real, parameter :: root = 1.0       ! root depth, soil and species specific (m)

real, parameter :: Lm = 0.02        ! Leaf dimension (m)
real, parameter :: Y = 6            ! Threshold (Y) in AFstY, nmol O3 m-2 s-1


!Campbell parameters

real, parameter :: soil_B = 3.31    !from Tuzet et al 2003
                                    !Sandy loam = 3.31, Silt loam = 4.38, Loam = 6.58
                                    !!clay loam = 7 (estimated) 

real, parameter :: SWP_AE = -0.00091 ! water potential at air entry (MPa)
                                              ! sandy loam = -0.00091, silt loam, -0.00158, loam, -0.00188
                                              ! clay loam = -0.00588 (estimated)           

real, parameter :: SWC_sat = 0.4    ! saturated water content m3/m3.  This is always 0.4


! =============================================
! Calculated deposition, Rsur and go3 variables
! =============================================

real :: SAI              ! Stand Area Indea m2/m2
real :: LAI              ! Leaf Area Index m2/m2

real :: Gsto             ! Bulk stomatal conductance mmol O3 m-2 PLA s-1
real :: Gsto_PEt         ! Bulk stomatal conductance mmol O3 m-2 PLA s-1
				 ! assuming no soil water limit
real :: Gsto_sm          ! Bulk stomatal conductance s/m
real :: gO3              ! Upper leaf stomatal conductnce mmol O3 m-2 PLA s-1
real :: go3_prevhr       ! Logs go3 of previous hour for sumVPD calculation
real :: leaf_gO3         ! Upper leaf stomatal condctance m/s
real :: leaf_rO3         ! Upper leaf stoamtal resistance s/m
real :: leaf_r           ! leaf resistance s/m
real :: fO3              ! ozone function reducing gsto

real :: fphen            ! phenology related bulk g
real :: flight           ! Canopy average gsto in relation to canopy light
real :: ftemp            ! temperate related g
real :: bt               ! ftemp variable
real :: fVPD             ! VPD related g
real :: sumVPD           ! Sum of VPD over the course of a day for gsto estimation
real :: Rsto             ! average canopy leaf stomatal resistance to O3 in s/m
real :: fSWP             ! SWP related g
real :: Rinc             ! In-canopy aerodynamic reistance
real :: Rsur             ! Surface resistance to ozone in s/m
real :: Ftot             ! Total ozone flux to vegetated surface in nmol O3 m-2 PLA s-1

real :: leaf_fphen       ! phenology related to leaf g
real :: leaf_flight      ! light related g
real :: leaf_rb          ! leaf level rb in s/m
real :: leaf_gb          ! leaf level gb in m/s


! flight variables

real :: PARsun
real :: PARshade
real :: LAIsunfrac
real :: sinB            ! B = solar elevation angle complement
                        ! of zenith angle
real :: sunLAI          ! sunlit LAI
real :: f_shade         ! shade-leaf contribution to f_light

real :: Rlow            ! Low temperature resistance(af.Wesely, 1989)
real :: Rgs             ! Non vegetative surface resistance
				! including low temperature and snow


real :: Vd     		! Deposition velocity of ozone (m/s)
real :: Fst   		! Upper leaf stomatal ozone flux (nmol O3 m-2 PLA s-1)
real :: AFstY 		! Accumulated stomatal flux above a threshold Y (mmol O3 m-2 PLA)
real :: AFst0           ! Accumulated stomatal flux above a threshold 0 (mmol O3 m-2 PLA) for fO3 calc.
real :: OT40   		! Ozone over 40 ppb over fphen period (ppm)
real :: AOT40  		! AOT40 over bulk canopy growth period (ppm.hrs)


!===============================================================
! Read in data from file to estimate thermal time growth periods
!===============================================================


max_lines = 400000


open (unit=3, file="74_51", &
       status="old", action="read", position="rewind")

open (unit=8, file="Output_thermal", &
       status="replace", action="write", position="rewind")


! ****************************
! Initialize variables for SWP
! ****************************

   hour_count_7      = 0
   hour_count_8      = 0
   hour_count_9      = 0
   
   dd                = 1 

! Initialize other vaiables

   T_dd       = 0
   T_sum      = 0
   T_avg      = 0
   SGS        = 400
   Astart     = 400
   Mid_anthesis = 400
   Aend       = 400

do i=1, max_lines

read(unit=3, fmt=*, iostat=ios) emep_i, emep_j, lat, mm, mdd, hr, Ts_c, precip, &
                                Idrctt, Idfuse, uh, ustar, VPD, O3_ppb_zR, &
                                O3_ppb_ch



if (ios>0) then
print *, "Error during opening"
exit

else if (ios<0) then
print *, "End of file thermal reached :o)"
exit

end if

!===========
!use variables otherwise not used to avoid error message
!===========

mm = mm
mdd = mdd
precip = precip
Idrctt = Idrctt
Idfuse = Idfuse
uh = uh
ustar = ustar
VPD = VPD
O3_ppb_zR = O3_ppb_zR
O3_ppb_ch = O3_ppb_ch



hour_count_7  = hour_count_7 + 1

      if (hour_count_7 < 25) then

        dd = dd

        else if (hour_count_7 == 25) then

        dd = dd + 1

        hour_count_7 = 1

      end if


! =============================================
! Estimates growth periods based on thermal time 
! =============================================

! Calculate daily average temperature (T_dd)

! Thermal time for winter wheat. 
! Plant emergence (SGS) occurs once T_avg > 0oC after 1st Jan
! Astart occurs when T_sum = 875
! Mid_anthsis occurs when T_sum = 1075
! Aend occurs when T_sum = 1775

!================================
! Estimate T_avg (mean daily ToC)
!================================

hour_count_8  = hour_count_8 + 1

if (hour_count_8 < 25) then

        T_dd = T_dd + Ts_c 

        else if (hour_count_8 == 25) then

        T_dd = T_dd + Ts_c
        T_avg = T_dd/24
        T_dd = 0

        hour_count_8 = 1

end if


!===================================================================
! Estimates SGS based on thermal time
!===================================================================

if (T_avg > 0) then 

        SGS = min(dd, SGS)

else if (T_avg <= 0) then

        SGS = SGS

end if



if (T_avg < Tb) then
        T_avg = 0
else if (T_avg >= Tb) then 
        T_avg = T_avg

end if

!=============================================
!Accumulates T_sum only after beginning of SGS 
!=============================================


if (SGS == 400) then

T_sum = T_sum

else if (SGS < 400) then

   hour_count_9  = hour_count_9 + 1

      if (hour_count_9 < 25) then 

          T_sum = T_sum


      else if (hour_count_9 == 25) then 

          T_sum = T_sum + T_avg

          hour_count_9 = 1

end if
end if


!================================================================
!Accumulates T_sum for whole year for use with Mid_anthesis value
!================================================================


   hour_count_10  = hour_count_10 + 1

      if (hour_count_10 < 25) then 

          T_sum = T_sum


      else if (hour_count_10 == 25) then 

          T_sum = T_sum + T_avg
          hour_count_10 = 1

      end if

!===================================================
!Estimates Tsum from particular dds, not needed here
!===================================================
 
   if (T_sum > 875) then 

        Astart = min(dd, Astart)

   else if (T_sum <= 875) then
 
        Astart = Astart

   end if


if (T_sum > 1075) then 

        Mid_anthesis = min(dd, Mid_anthesis)

   else if (T_sum <= 1075) then
 
        Mid_anthesis = Mid_anthesis

   end if


if (T_sum > 1775) then 

        Aend = min(dd, Aend)

   else if (T_sum <= 1775) then

        Aend = Aend

   end if

        

EGS = Aend

! =====================
! write output to file
! =====================

write (unit=8, fmt=*) emep_i, emep_j, Ts_C, T_dd, T_avg, T_sum


if (dd == 366 .and. hr == 23) then

SGS = SGS
Astart = Astart
Mid_anthesis = Mid_anthesis
Aend = Aend
EGS = EGS

print *, SGS, Astart, Mid_anthesis, Aend, EGS

end if

end do

close(unit=3)
close(unit=8)




! ======================
! Read in data from file to run main program
! ======================

max_lines = 400000


open (unit=9, file="74_51", &
       status="old", action="read", position="rewind")

open (unit=8, file="Output_74_51", &
       status="replace", action="write", position="rewind")

open (unit=3, file="Output_thermal", &
       status="old", action="read", position="rewind")

! ****************************
! Initialize variables for SWP
! ****************************

   hour_count        = 0
   hour_count_1      = 0
   hour_count_2      = 0
   hour_count_3      = 0
   hour_count_4      = 0
   hour_count_5      = 0
   hour_count_6      = 0

   dd                = 1 

   Precip_dd         = 0
   precip_use        = 0
   Ei_use            = 0
   AEt_use           = 0
   AEt_dd            = 0
   PEt_use           = 0
   PEt_dd            = 0
   Ei_dd             = 0

   PM_AEt_dd         = 0
   PM_PEt_dd         = 0
   PM_PEt_use        = 0 
   PM_AEt_use        = 0   

   SMD               = 0
   WC                = 0
   Sn                = 0

! *******************************

! ===============================
! Calculate Wstar for medium soil
! ===============================

!SWPcomp_a = (exp(swp_a+(swp_b*clay)+(swp_c*sand**2)+(swp_d*sand**2*clay))*100)
!SWPcomp_b = swp_e+(swp_f*clay**2)+(swp_g*sand**2)+(swp_g*sand**2*clay)

!PWP = (((-SWP_min)*1000)/SWPcomp_a)**(1/SWPcomp_b)

SWP_min_vol = 1/(((SWP_min/SWP_AE)**(1/soil_B))/SWC_sat)

ASW = Fc_m - SWP_min_vol
Sn_star = ASW



! Initialize SWP variables, MPa (according to soil specific attributes)
! old swp curve (soil_a*0.01)*((FC_m/soil_bd))**soil_b/1000
! Saxton curve = -(SWPcomp_a*(FC_m**SWPcomp_b))/1000  
   

   SWP         = SWP_AE*((SWC_sat/FC_m)**soil_B)
   Sn_1        = Sn_star
   WC          = Fc_m - SWP_min_vol
   Per_vol     = Fc_m * 100 
   fSWP        = 1

print *, Sn_star, SWP, Sn_1, WC


! Initialize other vaiables

   gsto_mes   = 0
   leaf_r_mes = 0
   sumVPD     = 0
   AFstY      = 0
   AFst0      = 0
   fO3        = 0
   Fst        = 0
   LAIsunfrac = 0
   AOT40      = 0
   OT40       = 0
   AFstY_Rmes = 0


do i=1, max_lines


read(unit=3, fmt=*, iostat=ios) emep_i, emep_j, Ts_C, T_dd, T_avg, T_sum

SGS = EGS - 92  ! shouldn't matter for leaf claculations but just in case....


read(unit=9, fmt=*, iostat=ios) emep_i, emep_j, lat, mm, mdd, hr, Ts_c, precip, &
                                Idrctt, Idfuse, uh, ustar, VPD, O3_ppb_zR, &
                                O3_ppb_ch



if (ios>0) then
print *, "Error during main program opening"
exit

else if (ios<0) then
print *, "End of file main program reached :o)"
exit

end if



hour_count_1  = hour_count_1 + 1

      if (hour_count_1 < 25) then

        dd = dd

        else if (hour_count_1 == 25) then

        dd = dd + 1

        hour_count_1 = 1

      end if

! ==========================
! Estimte Rn_j
! ==========================

Rn_j = (Idrctt + Idfuse) / 0.0004

psurf = 1013.25      ! Assumed constant
Hd = 7               ! Assumed constant

AEt_use = AEt_use
PEt_use = PEt_use
PM_PEt_use = PM_PEt_use


! ==================
! Calculate surface density of dry air (rho)
! ==================

Tk = Ts_C+273.16
psurf = psurf*100     ! converts psurf from hPa to Pa
rho = psurf/(Rmass*Tk)

! ==================
! Calculate Monin-Obukhov Length (L)
! ==================

if (Hd == 0) then

Hd = 0.00000000001          ! Makes sure Hd is not equal to 0 

end if

L = -(Tk*ustar**3*rho*cp)/(k*g*Hd)


! ==================
! Calculate stability functions for heat
! ==================

zo = h*0.1
d = h*0.7

Ezd = (z-d)/L
Ezo = zo/L

! for (z-d) calculations

  if (Ezd >= 0) then

  Psi_h_zd = -5*Ezd
  Psi_m_zd = -5*Ezd

  Psi_m_zd = Psi_m_zd
  
  else if (Ezd < 0) then
 
  Xzd = (1-15*Ezd)**(0.25)
  Psi_m_zd = log(((1+Xzd**2)/2)*((1+Xzd)/2)**2)-2*ATAN(Xzd)+(PI/2)
  Psi_h_zd = 2*log((1+Xzd**2)/2)

end if

! for (zo) calculations

  if (Ezo >= 0) then

  Psi_h_zo = -5*Ezo
  Psi_m_zo = -5*Ezo 
  
  else if (Ezo < 0) then

  Xzo = (1-15*Ezo)**(0.25)

  Psi_m_zo = log(((1+Xzo**2)/2)*((1+Xzo)/2)**2)-2*ATAN(Xzo)+(PI/2)
  Psi_h_zo = 2*log((1+Xzo**2)/2)

  Psi_m_zo = Psi_m_zo

end if

! ====================
! Calculate Ra, atmospheric resistance, s/m
! ====================


Ra    = 1/(k*ustar)*log(((z-d)/(d+zo)) - Psi_h_zd + Psi_h_zo)

if (Ra < 0) then 
Ra = 0
end if


! ====================
! Calculate Uz1, wind speed at top of canopy, m/s
! ====================

!Uz1 = (ustar/k) * (log((h-d)/zo)- Psi_m_zd + Psi_m_zo)
!This needs checking so use EMEP canopy height windspeed


! ===============================
! Stops wind speed from being zero and allowing leaf level r_b to be estimated
! ===============================

   if (uh <= 0 ) then

     uh = 0.001

     else if (uh > 0) then

     uh = uh

   end if

! ==========================================================
! Calculate Rb, quasi-laminar boundary layer resistance, s/m
! ==========================================================


Rb = (2/(k*ustar)) * ((v/DO3/Pr)**(0.6666666666666))

! ===============
! Calculate Rsur
! ===============


! =============
! Calculate LAI
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
! Calculate SAI 
! =============

  
! The code below is for crops, for forest trees SAI = 1 + LAI (placed at end of 
! code to over-ride crop code...)

if (dd < SGS) then

  SAI = LAI

 else if (dd >= SGS .and. dd < SGS+Ls) then

  SAI = LAI+((5/3.5)-1)*LAI

 else if (dd > SGS+Ls .and. dd <= EGS) then

  SAI = LAI + 1.5

 else if (dd > EGS) then

 SAI = LAI

 end if



! =====================================
! Calculate bulk canopy GSto (and Rsto)
! =====================================

! RSto = [(gmax*Fphen*Flight*max{fmin, (ftemp*fVPD*fSWP)})/41000]-1
! where 41000 converts from mmol m-2 s-1 to in m/s


! ================
! Calculate fphen
! ================

if (dd < SGS) then
fphen = 0

else if (dd == SGS) then
fphen = fphen_a

else if (dd > SGS .and. dd < SGS+fphenS ) then
fphen =  fphen_b + (fphen_c - fphen_b) * (dd-Astart)/fphenS

else if (dd >= SGS + fphenS .and. dd < EGS - fphenE ) then
fphen =  fphen_c

else if ( dd >= EGS - fphenE .and. dd < EGS ) then
fphen =  fphen_d + ( fphen_c - fphen_d) *(EGS - dd)/fphenE

else if (dd >= EGS .and. dd <= EGS) then
fphen = fphen_d

else if (dd > EGS) then
fphen = 0

end if


! ================
! Calculate leaf_fphen
! ================


!if (dd < Astart) then
!leaf_fphen = 0

!else if (dd >= Astart .and. dd < Astart+leaf_fphenS ) then
!leaf_fphen =  leaf_fphen_b + (leaf_fphen_c - leaf_fphen_b) * (dd-Astart)/leaf_fphenS

!else if (dd >= Astart + leaf_fphenS .and. dd < Aend - leaf_fphenE ) then
!leaf_fphen =  leaf_fphen_c

!else if ( dd >= Aend - leaf_fphenE .and. dd < Aend ) then
!leaf_fphen =  leaf_fphen_d + ( leaf_fphen_c - leaf_fphen_d) *(Aend - dd)/ leaf_fphenE

!else if (dd >= Aend .and. dd <= EGS) then
!leaf_fphen = 0

!else if (dd > EGS) then
!leaf_fphen = 0

!end if

!===============================
! need to use thermal time model
!===============================


if (T_sum < 875) then 
leaf_fphen = 0

else if (T_sum >= 875 .and. T_sum < 1175) then
leaf_fphen = 1

else if (T_sum >=1175 .and. T_sum < 1600) then
leaf_fphen = ((1-0.7)*(1600-T_sum)/425)+0.7

else if (T_sum >= 1600 .and. T_sum < 1775) then
leaf_fphen = 0.7*((1775-T_sum)/175)

else if (T_sum >= 1775) then 
leaf_fphen = 0

end if


! ================
! Calculate Flight
! ================

! Calculate zenith angle

dec = 360*(dd+10)/365

Solar_dec = -23.4 * cos(dec*DEG2RAD)

hr_angle = 15 * (hr - 12)

SinB = (sin(lat*DEG2RAD)*sin(Solar_dec*DEG2RAD)) + (cos(lat*DEG2RAD)*cos(Solar_dec*DEG2RAD)*cos(hr_angle*DEG2RAD))


! *****************************
! calculate PARsun and PARshade
! *****************************
! N.B. This part of the algorithm seems to produce the "floating underflow"

if (sinB > 0 .and. LAI > 0) then

! N.B. Dave Simpson was using zen < 89.9 but this seemed to produce a
! floating underflow, if use < 88 the problem seems to be solved
! with no change to the results.

!   sinB = cos(zen*DEG2RAD)    ! uses EMEP output zen to estimate sinB
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

else if (sinB <= 0 .or. LAI == 0 .or. Idrctt == 0) then

  sinB = 0
  LAIsunfrac = 0
  PARshade = 0
  PARsun = 0

end if

! ********************************
! calculate Flight and leaf_flight
! ********************************

leaf_flight   = (1.0 - exp (-f_lightfac*((Idrctt + Idfuse)*Wm2_2uEPAR)))
! changed so relates directly to input data in Idrctt and Idiff from EMEP input)



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

! ==================
! Calculate sum VPD
! ==================

   hour_count_6  = hour_count_6 + 1

      if (hour_count_6 < 25) then

        sumVPD  = sumVPD + VPD

      else if (hour_count_6 == 25) then

        sumVPD = sumVPD + VPD
        sumVPD = 0
        sumVPD = VPD

        hour_count_6 = 1

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

  Rsto_PEt = 100000         				! to allow for negligible Rsto

  else if (Gsto_PEt > 0 .and. LAI > 0) then

  Rsto_PEt = 1/(Gsto_PEt / 41000)   		! potential leaf stomatal
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


Ei_1 = ((Delta)*(Rn_J-G_J))/(lamda)

Ei_2 = 3600* Pair * Cair * (VPD * 1000) / (Rb*0.61) / lamda

Ei_3 = delta + psychro                          ! for evaporation from a surface the penman equation uses  heat condutance / water conductance (gh/gw). There is no surface resistance to water loss so this can be simplified to gH ~= gw e.g. gH/gw = 1

Ei_hr = ((Ei_1 + Ei_2) / Ei_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method



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
              +((Rsto_PEt*0.61)/LAI))*0.0224 &
              *((Ts_c+Ts_K)/Ts_K)*10**6)

   end if


! ======================
! Penman Monteith method
! ======================

esat = 611 * EXP((17.27*Ts_c)/(Ts_c+273.16))

eact = esat - (VPD * 1000)                    ! VPD in kPa

Tvir = (Ts_c+273.16)/(1-(0.378*(eact/Psurf)))  

delta= ((4098*esat)/((Ts_c+273.16)**2)) 

lamda = (2501000-(2361*Ts_c)) 

psychro = 1630 * (Psurf/lamda)

Pair = (0.003486*(Psurf/Tvir))

Cair = (0.622*((lamda*psychro)/Psurf)) 

G_J = Rn_J*0.1


! =====================


ET_1 = ((Delta)*(Rn_J-G_J))/(lamda)

ET_2 = 3600* Pair * Cair * (VPD * 1000) / (Rb*0.61) / lamda

PET_3 = delta + psychro * (1+((Rsto_PEt*0.61/LAI))/(Rb*0.61))       ! Assume Ra = 0

PM_PEt_hr = ((ET_1 + ET_2) / PET_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method

AET_3 = delta + psychro * (1+((Rsto*0.61/LAI))/(Rb*0.61))           ! Assume Ra = 0

PM_AEt_hr = ((ET_1 + ET_2) / AET_3) / 1000           ! Penman Monteith in mm/day so divie by 1000 to 
                                                     ! give in m/day for comparison with old method
! =====================



! For daily Ei and AEt_use, "_use" term

!   hour_count_1  = hour_count_1 + 1

      if (hour_count_1 < 25) then

        Ei_dd  = Ei_dd + Ei_hr

!       dd = dd

        else if (hour_count_1 == 25) then

        Ei_use = Ei_dd
        Ei_dd = 0 + Ei_hr

!        dd = dd + 1

!        hour_count_1 = 1

      end if


   hour_count_2  = hour_count_2 + 1

     if (hour_count_2 < 25) then

      AEt_dd  = AEt_dd + AEt_hr
      PM_PET_dd = PM_PEt_dd + PM_PEt_hr
      PM_AET_dd = PM_AEt_dd + PM_AEt_hr

      else if (hour_count_2 == 25) then

      AEt_use = AEt_dd
      AEt_dd = 0 + AEt_hr

    

      PM_AEt_use = PM_AEt_dd
      PM_AEt_dd = 0 + PM_AEt_hr

      hour_count_2 = 1

    end if

   hour_count_5  = hour_count_5 + 1

     if (hour_count_5 < 25) then

      PEt_dd  = PEt_dd + PEt_hr

      else if (hour_count_5 == 25) then

      PEt_use = PEt_dd
      PEt_dd = 0 + PEt_hr

      PM_PEt_use = PM_PEt_dd
      PM_PEt_dd = 0 + PM_PEt_hr

      hour_count_5 = 1

    end if


 hour_count_3  = hour_count_3 + 1

   if (hour_count_3 < 25) then

     Sn = Sn


     else if (hour_count_3 == 25 .and. Precip_use == 0) then
 
     Sn = -((PM_AEt_use)/root)                          ! Uses Penman Monteith method                        
     hour_count_3 = 1

     else if (hour_count_3 == 25 .and. Precip_use > 0) then

  !allows at least 70% of P to recharge soil water directly

     Sn = (Precip_use * 0.7) + ((Precip_use * 0.3) - (min(Ei_use, (precip_use * 0.3))) )/root 

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
  
  WD = Sn_star - Sn_1
  WC = Fc_m - (WD)
  Per_vol = (Fc_m - WD) * 100
  ASW = (Fc_m - WD) * root
  SWP = SWP_AE*((SWC_sat/WC)**soil_B)

if (SWP < -4) then
   SWP = -4
end if

  SMD = (sn_star - sn_1) * root
  hour_count_4 = 1

 end if

! ==============================================
! Calculate f for next days Gsto calculations
! ==============================================

! fswp=1/(0.75+(SWP/(-0.25))**1.5)   ! sloped fSWP relationship better fit to wheat data
                                 ! (used to parameterise model)

! If using default DO3SE model use:

fswp = (1-fmin) / (SWP_min - SWP_max) * (SWP_min - SWP) + fmin
fsWP = max(fswp, fmin)




if (fswp > 1) then
fswp = 1
end if

fswp=1     ! for UK model runs for now as correct Penman monteith not included (14th April 2010)

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


! ===============================
! Estimate deposition velocity
! ===============================


Vd = (1/(Ra + Rb + Rsur))     ! in m/s


O3_nmol_ch = (1/(R*(Tk/(psurf/1000)))) * O3_ppb_ch * 48 * 20.833 
                                       ! This should be same as multi-layer O3_nmol_ch_multi

! =================================================
! Estimate total ozone flux (nmol O3 m-2 PLA s-1)
! =================================================




Ftot = O3_nmol_ch * Vd          ! in nmol O3 m-2 PLA s-1


! =========================================================
! Calculate ozone effects parameters (e.g. AFstY and AOT40)
! =========================================================


! Need to estimate upper canopy leaf gO3
! May want to use leaf_fphen.....


    gO3 = gmax * (min(leaf_fphen, fO3)) * leaf_flight * ftemp * fVPD * fSWP   ! in mmol O3 m-2 s-1

  
  if (sumVPD > VPDsum_crit .and. go3 < gO3_prevhr) then

    gO3 = gO3          ! in mmol O3 m-2 s-1

  
  else if (sumVPD > VPDsum_crit .and. go3 > gO3_prevhr) then

    gO3 = gO3_prevhr   ! in mmol O3 m-2 s-1


  end if


  if (hour_count_6 < 25) then

    go3_prevhr = gO3     ! Establishes gO3 for this hour for the following hours gO3 calculation in light of sumVPD

  else if (hour_count_6 == 25) then

    go3_prevhr = 0

  end if



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

        Fst = O3_nmol_ch * leaf_gO3 * (leaf_r/(leaf_rb + leaf_r))  ! Fst in nmol/m2/s

        end if

else if (gO3 == 0) then

Fst = 0

end if

! ========================
! Calculate Fst with Rmes
! ========================

! Boundary line formulations to estimate fmes

fmes_hr = 0.0000021943 * hr**5 - 0.0001360058 * hr**4 + 0.0029003988 * hr**3 - 0.0238 * hr**2 + 0.0548 * hr + 0.7775
 
fmes_O3 = -0.000000008 * O3_ppb_ch**4 - 0.000003 * O3_ppb_ch**3 + 0.00008 * O3_ppb_ch**2 - 0.0004 * O3_ppb_ch + 0.9998

if (fmes_O3 < fmin_mes) then
fmes_O3 = fmin_mes
end if

fmes_PAR = 0.0000001 * PARsun**2 - 0.0002 * PARsun + 0.7049

bt_mes = (T_max_mes-T_opt_mes)/(T_opt_mes-T_min_mes)

fmes_temp = ((Ts_c-T_min_mes)/(T_opt_mes-T_min_mes))*((T_max_mes-Ts_c)/(T_max_mes-T_opt_mes))**bt_mes
fmes_temp = max(fmes_temp, fmin_mes)

if (Ts_C > 20) then 
fmes_temp = 1
end if


fmes_VPD = ((1-fmin_mes)*(VPD_min_mes-VPD)/(VPD_min_mes-VPD_max_mes))+fmin_mes
fmes_VPD = max(fmes_VPD, fmin_mes)

if (fmes_VPD > 1) then
fmes_VPD = 1
end if

! Estimte gmes

gmes = (gmes_max - gmes_min) * (fmes_hr * fmes_O3 * fmes_PAR * fmes_temp * fmes_VPD) + gmes_min   ! in mmol m-2 s-1

gmes_ms = gmes / 41000     ! conductance in m/s
Rmes = 1/gmes_ms           ! resistance in s/m
Fst_mes = 0


if (go3 > 0) then 

gsto_mes = (leaf_gO3 * gmes_ms) / (leaf_gO3 + gmes_ms)   ! conductance in m/s
leaf_r_mes = leaf_rb + ((Rext * (leaf_ro3 + Rmes)) / (Rext + (leaf_r + Rmes)))
Fst_mes = O3_nmol_ch * (1/leaf_r_mes) * (gsto_mes/(gsto_mes + (1/Rext)))

else if (gO3 <= 0) then 

gsto_mes = 0
leaf_r_mes = 0
Fst_mes = 0

end if


Detox = Fst - Fst_mes


! ================================
! calculate AFstY for Y=6 and Rmes and fO3
! ================================

AFst0 = AFst0 + ((Fst*60*60)/1000000)

fO3 = ((1+(AFst0/11.5)**10)**(-1))


if (Fst <= Y) then

AFstY = AFstY

else if (Fst > Y) then

AFstY = AFstY + (((Fst-Y)*60*60)/1000000)  ! Cumulative Fst above Y in mmol/m2

end if

AFstY_Rmes = AFstY_Rmes + (((Fst_mes)*60*60)/1000000)  ! Cumulative Fst above Y in mmol/m2


! =================================
! calculate AOT40 over Fphen period
! =================================

if (O3_ppb_ch > 40) then

  OT40 = (O3_ppb_ch - 40) / 1000

else if (O3_ppb_ch <= 40) then

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


! =====================
! write output to file
! =====================

write (unit=8, fmt=*) emep_i, emep_j, lat, mm, mdd, dd, hr, Ra, Rb, Rsto, Rsur, Vd, Ftot, &
                      LAI, SAI, fphen, leaf_fphen, &
                      SWP, fswp, SMD, Per_vol, Sn_1, Sn, ASW, &
                      Gsto, gO3, O3_ppb_zR, O3_ppb_ch, Fst, AFstY, AOT40, SGS, EGS, Astart, Aend, &
                      flight, ftemp, fVPD, fSWP, leaf_flight, fO3, T_sum
                      

end do

close(unit=9)
close(unit=8)
close(unit=3)

end program DOSE

