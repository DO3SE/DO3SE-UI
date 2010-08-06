program farquar

! This program models the net assimilation rate of C3 plants according to a 
! popular model developed by Farquar (1980).

! ====================================================
! Model parameters
! ====================================================

! parameters considered (or defined) to be constant for all species

real, parameter :: R = 8.314472          !universal gas constant             [J/(K*mol)]
real, parameter :: p_O2 = 210	           !O2 partial pressure                [mmol/mol]
real, parameter :: E_K_C = 79430         !activation energy of K_C           [J/mol]            Medlyn2002
real, parameter :: E_K_O = 36380         !activation energy of K_O           [J/mol]            Medlyn2002
real, parameter :: E_R_d = 53000         !activation energy of R_d           [J/mol]            Leuning1995
real, parameter :: E_Gamma_star = 37830  !activation energy for C-comp-point [J/mol]            Medlyn2002
real, parameter :: K_C_25 = 404.9        !K.C at reference temperature 25    [micro mol/mol]    Medlyn2002				
real, parameter :: K_O_25 = 278.4        !K.O at reference temperature 25    [mmol/mol]         Medlyn2002
real, parameter :: R_d_20 = 0.32         !R_d at reference temperature 20    [micro mol/(m^2*s)]Leuning1995
real, parameter :: Gamma_star_25 = 42.75 !CO2 compensation point at T= 25    [micro mol/mol]    Medlyn2002
real, parameter :: Teta	= 0.95           !shape of J~Q determining factor    []                 Leuning1995
real, parameter :: H_a_jmax = 50300      !activation energy for J_max        [J/mol]            Leuning2002
real, parameter :: H_d_jmax = 152044     !deactivation energy for J_max      [J/mol]            Leuning2002
real, parameter :: H_a_vcmax = 73637     !activation energy for V_cmax       [J/mol]            Leuning2002
real, parameter :: H_d_vcmax = 149252    !deactivation energy for V_cmax     [J/mol]            Leuning2002
real, parameter :: S_V_vcmax = 486       !entropy terms                      [J/(mol*K)]        Leuning2002
real, parameter :: S_V_jmax = 495        !entropy terms                      [J/(mol*K)         Leuning2002



! species spedific model parameters

real :: alpha                            !efficiency light energy conversion [mol electrons/mol photons]
real :: g_0                              !Conductance with closed stomata    [micro mol/(m^2*s)]
real :: m                                !fudge factor                       []	
real :: V_cmax_25                        !value of Vcmax at 25 degrees C     [micro mol/(m^2*s)]
real :: J_max_25                         !values of Jmax at 25 degrees C     [micro mol/(m^2*s)]

! ====================================================
! Model variables
! ====================================================

! driving variables, e.g. input data

real :: c_i = 200                            !CO2 concentration inside stomata   [micromol/mol]
real :: T = 300                              !leaf temperature                   [K]
real :: Q =1800                              !irradiance (PAR)                   [micro mol photons /(m^2*s)]

! state variables
	
real :: A_n                             !netto assimilation rate            [micro mol/(m^2*s)]
real :: A_c                             !Rub. activity. lim. ass. rate      [micro mol/(m^2*s)]
real :: A_q                             !electr. transp. lim. ass. rate     [micro mol/(m^2*s)]
real :: Gamma_star                      !CO2 comp. point without day resp.  [micro mol/mol]
real :: R_d                             !day respiration rate               [micro mol/(m^2*s)]
real :: K_C                             !Michaelis constant CO2             [micro mol/mol]
real :: K_O                             !Michaelis constant O2              [micro mol/mol]
real :: J                               !Rate of electron transport         [micro mol/(m^2*s)]
real :: Gamma                           !CO2 compensation point             [micro mol/mol]
real :: J_max                           !Max rate of electron transport     [micro mol/(m^2*s)]
real :: V_cmax                          !Max catalytic rate of Rubisco      [micro mol/(m^2*s)]



! ====================================================
! Reading of species specific parameters
! ====================================================

open (unit = 9, status = "old", file = "mod_pars.txt",&
                         action = "read", position ="rewind")
read(unit = 9, fmt=*) alpha,g_0,m,V_cmax_25,J_max_25
close (unit = 9)

print *,"alpha =",alpha,"g_0 =",g_0,"m =",m,"Vcmax_25 =",V_cmax_25,&
                        "J_max_25 =",J_max_25

! ====================================================
! Reading of input data 
! ====================================================

open (unit = 8, status = "old", file = "input.csv",&
                         action = "read", position ="rewind")

open (unit = 7, status = "replace", file = "output.csv",&
                         action = "write", position ="rewind")

do i=1, 10000

  read (unit = 8, fmt=*,iostat=ios) c_i,T,Q

  if (ios>0) then
    print *, "Error during opening"
    close (unit = 7)
    close (unit = 8)
    exit
  else if (ios<0) then
    print *, "End of file reached"
    close (unit = 7)
    close (unit = 8)
    exit
  end if

! ====================================================
! Calculation process
! ====================================================


  Gamma_star = Gamma_star_25*exp((E_Gamma_star*(T-298))/(298*R*T))

  K_C        = K_C_25*exp((E_K_C*(T-298))/(298*R*T))					

  K_O        = K_O_25*exp((E_K_O*(T-298))/(298*R*T))

  R_d        = R_d_20*exp((E_R_d*(T-293))/(293*R*T))

  J_max      = J_max_25*exp((H_a_jmax*(T-298))/(298*R*T))*&
               (1+exp((298*S_V_jmax-H_d_jmax)/(298*R)))/&
               (1+exp((T*S_V_jmax-H_d_jmax)/(T*R)))

  V_cmax     = V_cmax_25*exp((H_a_vcmax*(T-298))/(298*R*T))*&
               (1+exp((298*S_V_vcmax-H_d_vcmax)/(298*R)))/&
               (1+exp((T*S_V_vcmax-H_d_vcmax)/(T*R)))

  J          = ((alpha*Q+J_max)-sqrt((alpha*Q+J_max)**2-4*(alpha*Q*J_max*Teta)))/&
               (2*Teta)

  A_c        = V_cmax *((C_i-Gamma_star)/(C_i + K_C*(1+(p_O2/K_O))))

  A_q        = J*(C_i-Gamma_star)/(4*(C_i+2*Gamma_star))

  A_n        = min(A_c,A_q)-R_d	





  write (unit = 7, fmt=*) A_c,A_q,A_n 
  print *,i,"iostatus=",ios,"c_i=",c_i,"T =",T,"Q =",Q,"A_n =",A_n

end do
close (unit = 7)
close (unit = 8)
end program farquar
