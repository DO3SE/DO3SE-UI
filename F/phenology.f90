module Phenology

    public :: Calc_LAI
    public :: Calc_SAI_Simple
    public :: Calc_SAI_Crops
    public :: Calc_fphen

contains 

    !==========================================================================
    ! LAI calculation based on growing season - uses polygon calculation
    !==========================================================================
    subroutine Calc_LAI()
        use Functions, only: Polygon
        use Params_Veg, only: SGS, EGS, Ls, Le, LAI_min, &
            LAI_max
        use Inputs, only: dd
        use Variables, only: LAI

        LAI = Polygon(SGS, SGS + Ls, EGS - Le, EGS, &
                        LAI_min, LAI_max, LAI_min, dd)
    end subroutine Calc_LAI

    !==========================================================================
    ! 'Simple' SAI calculation - SAI = LAI + 1 for grasses and trees
    !==========================================================================
    subroutine Calc_SAI_Simple()
        use Variables, only: LAI, SAI
        SAI = LAI + 1
    end subroutine Calc_SAI_Simple

    !==========================================================================
    ! SAI calculation for crops taking growing season into account
    !==========================================================================
    subroutine Calc_SAI_Crops()
        use Inputs, only: dd
        use Params_Veg, only: SGS, EGS, Ls
        use Functions, only: Polygon
        use Variables, only: LAI, SAI

        if ( dd < SGS .or. dd > EGS ) then
            SAI = LAI
        else if ( dd < SGS + Ls ) then      ! implicitly > SGS
            SAI = LAI + ((5/3.5) - 1)*LAI
        else                ! implicitly >= SGS + Ls .and. <= EGS
            SAI = LAI + 1.5
        end if
    end subroutine Calc_SAI_Crops

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
    !  0.0 |___|            <1> = fphen1, etc.                |___________
    !      |
    !      +--------------------------------------------------------------
    !      0   | <1> |       |<2>|         |<3>|       | <4>  |         365
    !          |             |                 |              |
    !         SGS       fphen_limA        fphen_limB         EGS
    !
    !                                Day of Year
    !==========================================================================
    subroutine Calc_fphen()
        use Functions, only: Polygon
        use Params_Veg, only: SGS, EGS, Astart, Aend, &
            fphen_a, fphen_b, fphen_c, fphen_d, fphenS, fphenE
        use Inputs, only: dd
        use Variables, only: fphen, leaf_fphen

        if ( dd <= SGS .or. dd > EGS ) then
            fphen = 0
        else if ( dd < Astart ) then
            fphen = fphen_a
        else if ( dd < Astart + fphenS ) then
            fphen = fphen_b + (fphen_c - fphen_b) * (dd - Astart)/fphenS
        else if ( dd < Aend - fphenE ) then
            fphen = fphen_c
        else if ( dd < Aend ) then
            fphen = fphen_d + (fphen_c - fphen_d) * (Aend - dd)/fphenE
        else
            fphen = fphen_d
        end if

        ! TODO: Change this to calculate fphen for upper canopy leaf?
        leaf_fphen = fphen
    end subroutine Calc_fphen

end module Phenology
