module Phenology

    public :: Calc_LAI
    public :: Calc_SAI_Simple
    public :: Calc_SAI_Wheat
    public :: Calc_fphen
    public :: Copy_leaf_fphen
    public :: Calc_leaf_fphen_Wheat

contains 

    !==========================================================================
    ! LAI calculation based on growing season - uses polygon calculation
    !
    !     |        LAI_b                        LAI_c
    !     |          ______________________________
    !  L  |         /                              \
    !  A  |        /                                \
    !  I  |       /                                  \
    !     |      /                                    \
    !     |     /            <1> = LAI_1               \
    !     |  LAI_a                                   LAI_d
    !     +--------------------------------------------------
    !          |<1> |                              | <2>|
    !         SGS                                      EGS
    !                       Day of year
    !==========================================================================
    subroutine Calc_LAI()
        use Params_Veg, only: SGS, EGS, LAI_a, LAI_b, LAI_c, LAI_d, LAI_1, LAI_2
        use Inputs, only: dd
        use Variables, only: LAI

        if (dd < SGS .or. dd > EGS) then
            LAI = 0
        else if (dd < (SGS + LAI_1)) then
            LAI = LAI_a + (LAI_b - LAI_a) * (dd - SGS) / LAI_1
        else if (dd < (EGS - LAI_2)) then
            LAI = LAI_b + (LAI_c - LAI_b) * (dd - (SGS + LAI_1)) / (EGS - SGS - LAI_1 - LAI_2)
        else if (dd <= EGS) then
            LAI = LAI_d + (LAI_c - LAI_d) * (EGS - dd) / LAI_2
        end if
    end subroutine Calc_LAI

    !==========================================================================
    ! 'Simple' SAI calculation - SAI = LAI + 1 for grasses and trees
    !==========================================================================
    subroutine Calc_SAI_Simple()
        use Variables, only: LAI, SAI
        SAI = LAI + 1
    end subroutine Calc_SAI_Simple

    !==========================================================================
    ! SAI calculation for wheat taking growing season into account
    !==========================================================================
    subroutine Calc_SAI_Wheat()
        use Params_Veg, only: SGS, EGS, LAI_1
        use Inputs, only: dd
        use Variables, only: LAI, SAI

        if ( dd < SGS .or. dd > EGS ) then
            SAI = LAI
        else if ( dd < SGS + LAI_1 ) then      ! implicitly > SGS
            SAI = LAI + ((5/3.5) - 1)*LAI
        else                ! implicitly >= SGS + Ls .and. <= EGS
            SAI = LAI + 1.5
        end if
    end subroutine Calc_SAI_Wheat

    !==========================================================================
    ! Calculate fphen, incorporating differing plant and leaf growth seasons
    !
    !      |          fphen_b                   fphen_d
    !  1.0 |         _________                 _________
    !      |        /         \               /         \
    !      |       /           \             /           \
    ! f    |      /             \  fphen_c  /             \
    ! p    |     /               \_________/               \
    ! h    |    / fphen_a                                   \
    ! e    |   |                                             \ fphen_e
    ! n    |   |                                              |
    !      |   |                                              |
    !  0.0 |___|            <1> = fphen_1, etc.               |___________
    !      |
    !      +--------------------------------------------------------------
    !      0   | <1> |       |<2>|         |<3>|       | <4>  |         365
    !          |             |                 |              |
    !         SGS       fphen_limA        fphen_limB         EGS
    !
    !                                Day of Year
    !==========================================================================
    subroutine Calc_fphen()
        use Params_Veg, only: SGS, EGS
        use Params_Veg, only: fphen_limA, fphen_limB, fphen_1, fphen_2, fphen_3, fphen_4
        use Params_Veg, only: fphen_a, fphen_b, fphen_c, fphen_d, fphen_e
        use Inputs,     only: dd
        use Variables,  only: fphen, leaf_fphen

        if (dd < SGS .or. dd > EGS) then
            fphen = 0.0
        else if (dd < (SGS + fphen_1)) then
            fphen = fphen_a + (fphen_b + fphen_a) * (dd - SGS) / fphen_1
        else if (dd < fphen_limA) then
            fphen = fphen_b
        else if (dd < (fphen_limA + fphen_2)) then
            fphen = fphen_b - (fphen_b - fphen_c) * (dd - fphen_limA) / fphen_2
        else if (dd < (fphen_limB - fphen_3)) then
            fphen = fphen_c
        else if (dd < fphen_limB) then
            fphen = fphen_d - (fphen_d - fphen_c) * (fphen_limB - dd) / fphen_3
        else if (dd < (EGS - fphen_4)) then
            fphen = fphen_d
        else if (dd <= EGS) then
            fphen = fphen_e + (fphen_d - fphen_e) * (EGS - dd) / fphen_4
        end if
    end subroutine Calc_fphen

    !==========================================================================
    ! Copy canopy fphen as leaf fphen
    !==========================================================================
    subroutine Copy_leaf_fphen()
        use Variables, only: fphen, leaf_fphen

        leaf_fphen = fphen
    end subroutine Copy_leaf_fphen

    !==========================================================================
    ! Calculate leaf_fphen for Wheat
    !==========================================================================
    subroutine Calc_leaf_fphen_Wheat()
        use Params_Veg, only: leaf_fphen_a, leaf_fphen_b, leaf_fphen_c, &
                              leaf_fphen_1, leaf_fphen_2, Astart, Aend
        use Inputs,     only: dd
        use Variables,  only: leaf_fphen

        if (dd < Astart .or. dd > Aend) then
            leaf_fphen = 0
        else if (dd < (Astart + leaf_fphen_1)) then
            leaf_fphen = leaf_fphen_a + (leaf_fphen_b - leaf_fphen_a) * (dd - Astart) / leaf_fphen_1
        else if (dd < (Aend - leaf_fphen_2)) then
            leaf_fphen = leaf_fphen_b
        else if (dd <= Aend) then
            leaf_fphen = leaf_fphen_c + (leaf_fphen_b - leaf_fphen_c) * (Aend - dd) / leaf_fphen_2
        end if
    end subroutine Calc_leaf_fphen_Wheat

end module Phenology
