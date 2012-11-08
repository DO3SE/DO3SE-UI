module Phenology

    public :: Latitude_SGS_EGS
    public :: Calc_LAI
    public :: Calc_SAI_Wheat
    public :: Calc_fphen
    public :: Calc_leaf_fphen_fixed_day

contains 

    !
    ! Latitude function for calculating start and end of growing season
    !
    subroutine Latitude_SGS_EGS(lat, SGS, EGS)
        real, intent(in) :: lat
        integer, intent(out) :: SGS, EGS

        SGS = nint(((lat - 50) * 1.5) + 105)
        EGS = nint(297 - ((lat - 50) * 2))
    end subroutine Latitude_SGS_EGS

    !==========================================================================
    ! LAI calculation based on growing season - uses polygon calculation
    !
    !     |        LAI_b                        LAI_c
    !     |          ______________________________
    !  L  |         /                              \
    !  A  |        /                                \
    !  I  |       /                                  \
    !     |      /                                    \
    !     |_____/            <1> = LAI_1               \_____
    !     |  LAI_a                                   LAI_d
    !     +--------------------------------------------------
    !          |<1> |                              | <2>|
    !         SGS                                      EGS
    !                       Day of year
    !==========================================================================
    subroutine Calc_LAI()
        use Parameters, only: SGS, EGS, LAI_a, LAI_b, LAI_c, LAI_d, LAI_1, LAI_2
        use Inputs, only: dd
        use Variables, only: LAI

        if (dd < SGS) then
            LAI = LAI_a - (LAI_a - LAI_d) * (SGS - dd) / (365 - EGS + SGS)
        else if (dd < (SGS + LAI_1)) then
            LAI = LAI_a + (LAI_b - LAI_a) * (dd - SGS) / LAI_1
        else if (dd < (EGS - LAI_2)) then
            LAI = LAI_b + (LAI_c - LAI_b) * (dd - (SGS + LAI_1)) / (EGS - SGS - LAI_1 - LAI_2)
        else if (dd <= EGS) then
            LAI = LAI_d + (LAI_c - LAI_d) * (EGS - dd) / LAI_2
        else if (dd > EGS) then
            LAI = LAI_d + (LAI_a - LAI_d) * (dd - EGS) / (365 - EGS + SGS)
        end if
    end subroutine Calc_LAI

    !==========================================================================
    ! SAI calculation for wheat taking growing season into account
    !==========================================================================
    subroutine Calc_SAI_Wheat()
        use Parameters, only: SGS, EGS, LAI_1
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
        use Parameters, only: SGS, EGS
        use Parameters, only: fphen_limA, fphen_limB, fphen_1, fphen_2, fphen_3, fphen_4
        use Parameters, only: fphen_a, fphen_b, fphen_c, fphen_d, fphen_e
        use Inputs,     only: dd
        use Variables,  only: fphen

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
    ! Calculate leaf_fphen using fixed-day method
    !==========================================================================
    subroutine Calc_leaf_fphen_fixed_day()
        use Parameters, only: leaf_fphen_a, leaf_fphen_b, leaf_fphen_c, &
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
    end subroutine Calc_leaf_fphen_fixed_day

end module Phenology
