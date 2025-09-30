Program Penman_Monteith

!template for calculating potential evapotranspiration using Penman Monteith method
!Input data from Easter Bush

! =========================================
! Imported local variables, i.e. input data
! =========================================

integer :: yy   ! year
integer :: mm   ! month
integer :: mdd  ! day of month
integer :: dd   ! day of year
integer :: hr   ! hour of day
real :: LAI     ! measured LAI
real :: CH      ! measured canopy height
real :: Psurf   ! surface air pressure (kPa)
real :: precip  ! measured precipitation (mm)
real :: Ts_c    ! surface air temperature in oC
real :: VPD     ! Vapour pressure deficit (kPa)
real :: Ra      ! aerodynamic resistance at 1m (s m-1)
real :: Rsto      ! canopy resistance incoporating fSWP (s m-1) from DO3SE code
real:: Gsto_PEt  ! Canopy conductance without fSWP (m s-1) from DO3SE code
real :: Rn      ! Net radiation (MJ m-2 h-1) This is taken from the Rn derivation module
real :: G       ! soil heat flux (MJ m-2 h-1) If G is not input see derivation below





! =========================================
! variables required for P-M equation
! =========================================

real :: PET     ! potential evapotranspiration (mm h-1)
real :: PET1    ! first term in potential PM equation
real :: PET2    ! second term in potential PM equation
real :: PET3    ! third term in potential PM equation
real :: AET     ! Acutal evapotranspiration (mm h-1)
real :: AET1    ! first term in actual PM equation
real :: AET2    ! second term in actual PM equation
real :: AET3    ! third term in actual PM equation
real :: delta   ! slope of vapour pressure curve (Pa C-1)
real :: lamda   ! latent heat of vapourisation (J kg-1)
real :: psychro ! psychrometric constant
real :: Pair    ! air density (kg cm-3)
real :: Cair    ! heat capacity of moist air (J g-1 C-1)
real :: esat    ! saturation vapour pressure (Pa)
real :: eact    ! actual vapour pressure (Pa)
real :: Tvir    ! virtual temperature (K)

integer :: i, max_lines, ios

! ======================
! Read in data from file
! ======================

max_lines = 400000


open (unit=9, file="EB full data", &
       status="old", action="read", position="rewind")

open (unit=8, file="EB full data output", &
       status="replace", action="write", position="rewind")


do i=1, max_lines

read(unit=9, fmt=*, iostat=ios) yy, mm, mdd, dd, hr, LAI, CH, Psurf, precip, &
                                  Ts_c, Rn, G,VPD, Ra, Rc

if (ios>0) then
print *, "Error during opening"
exit

else if (ios<0) then
print *, "End of file reached :o)"
exit

end if

! =========================================
! define terms
! =========================================

yy = yy
hr = Hr
CH = CH


Rn_J = Rn*1000000
Psurf_pa = Psurf*1000
VPD_pa = Psurf*1000

! if G is input then
!G_J = G*1000000
!if G is not it can be derived
!G_J = Rn_J*0.1


esat = 611 * EXP((17.27*Ts_c)/(Ts_c+273.3))
eact = esat - VPD_pa
Tvir = (Ts_c+273.3)/(1-(0.378*(eact/Psurf_pa)))
delta= ((4098*esat)/((Ts_c+273.3)**2)) 
lamda = (2.501-(0.002361*Ts_c)) * 1000000
psychro = 1630 * (Psurf_pa/lamda)
Pair = (0.003486*(Psurf_pa/Tvir))
Cair = (0.622*((lamda*psychro)/Psurf_pa)) 




! =========================================
! AET calculate term 1
! =========================================

AET1 = (Delta*(Rn_J-G_J))/lamda




! =========================================
! AET calculate term 2
! =========================================


AET2 = 3600* Pair * Cair* VPD_pa / Rsto / lamda


! =========================================
! AET calculate term 3
! =========================================

AET3 = delta + psychro * (1+Rsto/Ra)

! =========================================
! calculate AET
! =========================================

AET = (AET1 + AET2) / AET3





! =========================================
! PET calculate term 1
! =========================================

PET1 = (Delta*(Rn-G))/lamda


! =========================================
! PET calculate term 2
! =========================================


PET2 = 3600* Pair * Cair* VPD / (1/Gsto_PEt) / lamda


! =========================================
! AET calculate term 3
! =========================================

PET3 = delta + psychro * (1+(1/Gsto_PEt)/Ra)

! =========================================
! calculate AET
! =========================================

PET = (PET1 + PET2) / PET3


! =====================
! write output to file
! =====================

write (unit=8, fmt=*) yy, mm, mdd, dd, hr, LAI, Psurf, precip, Ts_c, Rn, G, &
                      VPD, Ra, Rc, delta, lamda, psychro, &
                      Pair, Cair, esat, eact, Tvir, AET1, AET2, AET3, AET, &
                      AET1, AET2, AET3, AET

end do

close(unit=9)
close(unit=8)


End program Penman_Monteith


