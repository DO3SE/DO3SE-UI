module Pn_Gsto

    implicit none

    public :: Calc_Gsto_Pn

    ! parameters considered (or defined) to be constant for all species
    real, parameter :: R = 8.314472          !universal gas constant             [J/(K*mol)]
    real, parameter :: p_O2 = 210.0          !O2 partial pressure                [mmol/mol]
    real, parameter :: E_K_C = 79430.0       !activation energy of K_C           [J/mol]            Medlyn2002
    real, parameter :: E_K_O = 36380.0       !activation energy of K_O           [J/mol]            Medlyn2002
    real, parameter :: E_R_d = 53000.0       !activation energy of R_d           [J/mol]            Leuning1995
    real, parameter :: E_Gamma_star = 37830.0 !activation energy for C-comp-point [J/mol]            Medlyn2002
    real, parameter :: K_C_25 = 404.9        !K.C at reference temperature 25    [micro mol/mol]    Medlyn2002
    real, parameter :: K_O_25 = 278.4        !K.O at reference temperature 25    [mmol/mol]         Medlyn2002
    real, parameter :: R_d_20 = 0.32         !R_d at reference temperature 20    [micro mol/(m^2*s)]Leuning1995
    real, parameter :: Gamma_star_25 = 42.75 !CO2 compensation point at T= 25    [micro mol/mol]    Medlyn2002

    ! species spedific model parameters (that don't tend to have species specific
    ! values, others are in parameters.f90)
    real :: alpha = 0.3                      !efficiency light energy conversion [mol electrons/mol photons]
    real :: Teta = 0.95                      !shape of J~Q determining factor    []
    real :: H_a_jmax = 50300                 !activation energy for J_max        [J/mol]
    real :: H_d_jmax = 152044                !deactivation energy for J_max      [J/mol]
    real :: H_a_vcmax = 73637                !activation energy for V_cmax       [J/mol]
    real :: H_d_vcmax = 149252               !deactivation energy for V_cmax     [J/mol]
    real :: S_V_vcmax = 486                  !entropy terms                      [J/(mol*K)]
    real :: S_V_jmax = 495                   !entropy terms                      [J/(mol*K)

    ! debug outputs
    real, public, save :: gsto_final, pngsto_l, pngsto, pngsto_c, pngsto_PEt
    real, public, save :: pngsto_An

contains

    subroutine Calc_Gsto_Pn()
        use Constants, only: Ts_K
        use Inputs, only: c_a => CO2, Q => PAR, u => uh, h_a => RH, Ts_C, Tleaf_C => Tleaf
        use Parameters, only: fmin, gmorph, d => Lm, g_sto_0, m, V_cmax_25, J_max_25
        use Variables, only: LAI, fphen, fO3, fXWP, leaf_fphen

        real :: T_air, T_leaf

        ! state variables
        real :: A_n                             !netto assimilation rate            [micro mol/(m^2*s)]
        real :: A_c                             !Rub. activity. lim. ass. rate      [micro mol/(m^2*s)]
        real :: A_q                             !electr. transp. lim. ass. rate     [micro mol/(m^2*s)]
        real :: Gamma_star                      !CO2 comp. point without day resp.  [micro mol/mol]
        real :: R_d                             !day respiration rate               [micro mol/(m^2*s)]
        real :: K_C                             !Michaelis constant CO2             [micro mol/mol]
        real :: K_O                             !Michaelis constant O2              [micro mol/mol]
        real :: J                               !Rate of electron transport         [micro mol/(m^2*s)]
        real :: ratio                           !TODO: ???
        real :: Gamma                           !CO2 compensation point             [micro mol/mol]
        real :: J_max                           !Max rate of electron transport     [micro mol/(m^2*s)]
        real :: V_cmax                          !Max catalytic rate of Rubisco      [micro mol/(m^2*s)]
        real :: e_sat_i                         !internal saturation vapour pressure[Pa]
        real :: g_bl                            !two sided bound.l. conduct., vapour[micro mol/(m^2s)]
        real :: g_sto                           !two sided stomatal conduct.,vapour [micro mol/(m^2s)]
        real :: g_tot                           !TODO: ???
        real :: h_s                             !relative humidity at leaf surface  [decimal fraction]
        real :: c_s                             !CO2 concentration at leaf surface  [micromol/mol]
        real :: c_i                             !CO2 concentration inside stomata   [micromol/mol]
        real :: e_a                             !ambient vapour pressure            [Pa]


        ! iteration parameters

        integer :: iterations                   !number of the iterations bofore convergence
        real :: c_i_sup                         !CO2 concentration inside stomata possible through supply
        integer :: i,k                          !loop parameters

        T_air = Ts_C + Ts_K
        T_leaf = Tleaf_C + Ts_K

        ! Calculation of the model variables which are only
        ! dependend on environmental conditions:

        Gamma_star = Gamma_star_25*exp((E_Gamma_star*(T_leaf-298))/(298*R*T_leaf))

        K_C        = K_C_25*exp((E_K_C*(T_leaf-298))/(298*R*T_leaf))

        K_O        = K_O_25*exp((E_K_O*(T_leaf-298))/(298*R*T_leaf))

        R_d        = R_d_20*exp((E_R_d*(T_leaf-293))/(293*R*T_leaf))

        J_max      = J_max_25*exp((H_a_jmax*(T_leaf-298))/(298*R*T_leaf))*&
                     (1+exp((298*S_V_jmax-H_d_jmax)/(298*R)))/&
                     (1+exp((T_leaf*S_V_jmax-H_d_jmax)/(T_leaf*R)))

        V_cmax     = V_cmax_25*exp((H_a_vcmax*(T_leaf-298))/(298*R*T_leaf))*&
                     (1+exp((298*S_V_vcmax-H_d_vcmax)/(298*R)))/&
                     (1+exp((T_leaf*S_V_vcmax-H_d_vcmax)/(T_leaf*R)))

        J          = ((alpha*Q+J_max)-sqrt((alpha*Q+J_max)**2-4*&
                     (alpha*Q*J_max*Teta)))/(2*Teta)



        e_sat_i    = 613.75*exp((17.502*(T_leaf-273.16))/(240.07+T_leaf-273.16))

        e_a        = h_a*613.75*exp((17.502*(T_air-273.15))/(240.97+T_air-273.15))

        ratio        = (9.81*abs(T_leaf-T_air))/((u**2)*(T_leaf+T_air/2))

        Gamma        = (Gamma_star+(K_C*R_d*(1+(p_O2/K_O))/V_cmax))/&
                       (1-(R_d/V_cmax))

        !aproximates the boundary layer conductance for forced convection
        !and sets the !conductance to a fixed value during free convection:

        if (ratio <= 0.1) then
            g_bl     = 2*0.147*sqrt(u/d)*1e6
        else
            g_bl     = 1.5*1e6
        end if

        !print *, Gamma_star,K_C,K_O,R_d,J_max,V_cmax
        !print *, J,e_sat_i,e_a,ratio
        !print *, Gamma,p_O2

        !The following loop guesses a start value for c_i and tests whether
        !it satisfies all the relevant restrictions. If not a new value for
        !c_i is tested:

        c_i         = 0.0

        do k=1,50

            A_c        = V_cmax *((c_i-Gamma_star)/(c_i + K_C*(1+(p_O2/K_O))))

            A_q        = J*(c_i-Gamma_star)/(4*(c_i+2*Gamma_star))

            A_n        = min(A_c,A_q)-R_d

            c_s        = c_a-(A_n*(1.37/g_bl))

            h_s        = (g_sto*e_sat_i+g_bl*e_a)/(e_sat_i*(g_sto+g_bl))

            g_sto      = g_sto_0 + ( m * A_n *(h_s/(c_s - Gamma)))*1e6

            g_tot      = 1/(1.6/g_sto+1.3/g_bl)

            c_i_sup    = c_a-((A_n/g_tot)*1e6 )

            !exits the loop when c_i calculated with both ways meet the convergence
            !criterium:

            iterations = k
            if (abs(c_i - c_i_sup) < 0.001) then
                exit
            end if

            !Guesses a new c_i as the mean of the first guess and c_i resulting from
            !the supply function:

            c_i      = c_i-(c_i-c_i_sup)/2

        end do

        ! Calculate final stomatal conductances
        gsto_final = max(0.0, g_sto / 1000.0)

        pngsto_l = gsto_final * min(leaf_fphen, fO3) * max(fmin, fXWP)
        pngsto = gsto_final * gmorph * fphen * max(fmin, fXWP)
        pngsto_c = pngsto * LAI
        pngsto_PEt = gsto_final * fphen * LAI

        pngsto_An = A_n


        !write (unit = 7, fmt=*) iterations,",",c_i,",",A_n,",",g_sto
        !print *,i,"iterations=",iterations,"c_i=",c_i,"A_n =",A_n,"g_sto =",g_sto
    end subroutine Calc_Gsto_Pn

end module Pn_Gsto
