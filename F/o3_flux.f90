module O3_Flux_mod

    public :: Calc_Vd, Calc_O3_Concentration, Calc_Ftot

contains

    subroutine Calc_Vd()
        use Variables_mod, only: Vd, Ra_O3, Rb, Rsur

        Vd = 1 / (Ra_O3 + Rb + Rsur)
    end subroutine Calc_Vd

    subroutine Calc_O3_Concentration()
        use Inputs_mod, only: O3_ppb_zR
        use Variables_mod, only: O3_ppb, O3_nmol_m3, Ra_O3, Vd

        O3_ppb = O3_ppb_zR * (1 - (Ra_O3 * (Vd)))
        O3_nmol_m3 = O3_ppb * 41.67   ! Estimates ozone concentration at canopy height 
                                      ! in nmol/m3; N.B> need to do proper conversion
                                      ! to include changes in T and P but no P in flux tower data......
    end subroutine Calc_O3_Concentration

    subroutine Calc_Ftot()
        use Variables_mod, only: Ftot, O3_nmol_m3, Vd

        Ftot = O3_nmol_m3 * Vd
    end subroutine Calc_Ftot

end module O3_Flux_mod
