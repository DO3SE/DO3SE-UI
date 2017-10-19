module Pn_Gsto

    implicit none

    public :: Calc_Gsto_Pn
    public :: leaf_temp_de_Boeck
    public :: saturated_vapour_pressure

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
    real, parameter :: T0 = 273.15

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

    pure real function saturated_vapour_pressure(Ts_C)
        real, intent(in) :: Ts_C    !< Surface air temperature (degrees C)

        saturated_vapour_pressure = 0.611 * exp(17.27 * Ts_C / (Ts_C + 237.3))
    end function saturated_vapour_pressure

pure function leaf_temp_de_Boeck(R, e_a, T_air, initial_T_leaf, P, u, g_vs, hypostomatous, d, albedo, cloud_cover, &
                                   balance_threshold, adjustment_factor, max_iterations) result(T_leaf)
    real, intent(in) :: R                   !< Global radiation (W m-2)
    real, intent(in) :: e_a                 !< Vapour pressure (Pa)
    real, intent(in) :: T_air               !< Air temperature (degrees C)
    real, intent(in) :: initial_T_leaf      !< T_leaf starting value (degrees C)
    real, intent(in) :: P                   !< Air pressure (Pa)
    real, intent(in) :: u                   !< Wind speed (m s-1)
    real, intent(in) :: g_vs                !< Stomatal conductance to water vapour (mol m-2 s-1)
    logical, intent(in) :: hypostomatous    !< Are leaves hypostomatous?
    real, intent(in) :: d                   !< Leaf characteristic dimension (m)
    real, intent(in) :: albedo              !< Surface albedo (fraction)
    real, intent(in) :: cloud_cover         !< Cloud cover (fraction)
    real, intent(in) :: balance_threshold   !< Threshold within which to accept leaf energy balance
    real, intent(in) :: adjustment_factor   !< Multiplier for energy balance based T_leaf adjustments
    integer, intent(in) :: max_iterations   !< Maximum iteration count

    real :: T_leaf    !< Output: Leaf temperature (degrees C)

    ! Stefan-Boltzmann constant, W m-2 K-4 (Campbell & Norman (1998), p281, table A5)
    real, parameter :: SBC = 5.670373e-8
    ! Specific heat capacity of dry air, J mol-1 C-1 (Campbell & Norman (1998), p279, table A1)
    real, parameter :: c_p = 29.3

    ! Leaf short-wave absorptivity (de Boeck (2012); from Campbell & Norman (1998), p153, in text)
    real, parameter :: alpha_s_leaf = 0.5
    ! Leaf long-wave absorptivity (de Boeck, 2012)
    real, parameter :: alpha_l_leaf = 0.97
    ! Soil long-wave emissivity (de Boeck, 2012)
    real, parameter :: eps_l_soil = 0.945
    ! Leaf long-wave emissivity (de Boeck, 2012)
    real, parameter :: eps_l_leaf = 0.97

    real :: rho_s_soil, VPL, eps_ac, eps_l_sky, lam, T_soil, T_leaf_adjust, g_Ha, g_vb, g_v, e_s_Tleaf
    real :: R_s_in, R_l_in, R_l_out, H, lam_E, energy_balance
    integer :: i

    ! Soil short-wave reflectivity
    rho_s_soil = albedo
    ! Water vapour path length (de Boeck 2012)
    VPL = 46.5 * ((0.01 * e_a) / (T_air + T0))
    ! Clear sky emissivity (de Boeck 2012)
    eps_ac = 1 - (1 + VPL) * exp(-(1.2 + 3.0 * VPL)**0.5)
    ! Sky long-wave emmisivity (de Boeck (2012); from Campbell & Norman (1998), p164, eq. 10.12)
    eps_l_sky = (1 - 0.84 * cloud_cover) * eps_ac + 0.84 * cloud_cover
    ! Latent heat of vapourisation, J mol-1 (de Boeck (2012))
    lam = -42.575 * T_air + 44994

    ! Assume soil temperature is equal to air temperature
    ! TODO: use the banded estimate from de Boeck (2012)?
    T_soil = T_air

    ! Starting point
    T_leaf = initial_T_leaf
    T_leaf_adjust = 0.0

    do i = 1, max_iterations
      ! Apply adjustment (from previous iteration)
      T_leaf = T_leaf + T_leaf_adjust

      ! Boundary layer conductances (de Boeck (2012))
      ! XXX: Assume forced convection:
      g_Ha = 1.4 * 0.135 * sqrt(u / d)
      g_vb = 1.4 * 0.147 * sqrt(u / d)

      ! Total conductivity to water vapour
      if (hypostomatous) then
        g_v = combined_leaf_conductance(g_vs, 0.0, g_vb)
      else
        g_v = combined_leaf_conductance(g_vs, g_vs, g_vb)
      end if

      ! Saturated vapour pressure for leaf temperature, Pa
      e_s_Tleaf = saturated_vapour_pressure(T_leaf) * 1000  ! Converted from kPa to Pa

      ! Absorbed short-wave (direct on top of leaf, reflected from soil on underside) (de Boeck (2012))
      R_s_in = (0.5 * R * alpha_s_leaf) + (0.5 * R * rho_s_soil * alpha_s_leaf)

      ! Absorbed long-wave (emitted from soil on underside, emitted from sky on top) (de Boeck (2012))
      R_l_in = (0.5 * alpha_l_leaf * eps_l_soil * SBC * (T_soil + T0)**4) + &
               (0.5 * alpha_l_leaf * eps_l_sky * SBC * (T_air + T0)**4)

      ! Emitted long-wave (de Boeck (2012))
      R_l_out = eps_l_leaf * SBC * (T_leaf + T0)**4

      ! Sensible heat flux (de Boeck (2012))
      H = g_Ha * c_p * (T_leaf - T_air)

      ! Latent heat flux (de Boeck (2012))
      lam_E = lam * g_v * (e_s_Tleaf - e_a) / P

      ! Energy balance equation (de Boeck (2012))
      energy_balance = R_s_in + R_l_in - R_l_out - H - lam_E

      if (abs(energy_balance) <= balance_threshold) then
        exit
      else
        T_leaf_adjust = energy_balance * adjustment_factor
      end if
    end do
  contains
    pure function combined_leaf_conductance(gs_ab, gs_ad, ga) result(g)
      real, intent(in) :: gs_ab   !< Abaxial stomatal conductance (mol m-2 s-1)
      real, intent(in) :: gs_ad   !< Adaxial stomatal conductance (mol m-2 s-1)
      real, intent(in) :: ga      !< Boundary layer conductance (mol m-2 s-1)
      real :: g     !< Output: combined leaf conductance (mol m-2 s-1)

      g = (0.5 * gs_ab * ga / (gs_ab + ga)) + (0.5 * gs_ad * ga / (gs_ad + ga))
    end function combined_leaf_conductance
  end function leaf_temp_de_Boeck

    subroutine Calc_Gsto_Pn()
        use Constants, only: Ts_K
        use Inputs, only: c_a => CO2, Q => PAR, uh, h_a => RH, Ts_C, Tleaf_C => Tleaf
        use Parameters, only: fmin, gmorph, d => Lm, g_sto_0, m, V_cmax_25, J_max_25
        use Variables, only: LAI, fphen, fO3, fXWP, leaf_fphen

        real :: T_air, T_leaf, u

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
        u = max(0.01, uh)

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
