module Options

    integer, public, parameter :: sai_equals_lai = 1
    integer, public, parameter :: sai_forest     = 2
    integer, public, parameter :: sai_wheat      = 3
    integer, public, save :: sai_method = sai_equals_lai

    integer, public, parameter :: rn_use_input  = 1
    integer, public, parameter :: rn_calculate  = 2
    integer, public, save :: rn_method = rn_use_input

    integer, public, parameter :: leaf_fphen_equals_fphen = 1
    integer, public, parameter :: leaf_fphen_fixed_day    = 2
    integer, public, parameter :: leaf_fphen_use_input    = 3
    integer, public, parameter :: leaf_fphen_thermal_time = 4
    integer, public, save :: leaf_fphen_method = leaf_fphen_equals_fphen

    integer, public, parameter :: ra_simple         = 1
    integer, public, parameter :: ra_with_heat_flux = 2
    integer, public, save :: ra_method = ra_simple

    integer, public, parameter :: tleaf_use_input        = 1
    integer, public, parameter :: tleaf_estimate = 2
    integer, public, save :: tleaf_method = tleaf_use_input

    integer, public, parameter :: gsto_multiplicative = 1
    integer, public, parameter :: gsto_photosynthetic = 2
    integer, public, save :: gsto_method = gsto_multiplicative

    integer, public, parameter :: fo3_disabled = 1
    integer, public, parameter :: fo3_wheat    = 2
    integer, public, parameter :: fo3_potato   = 3
    integer, public, save :: fo3_method = fo3_disabled

    integer, public, parameter :: fswp_input = 1
    integer, public, parameter :: fswp_exponential = 2
    integer, public, parameter :: fswp_linear      = 3
    integer, public, save :: fswp_method = fswp_exponential

    integer, public, parameter :: lwp_non_steady_state = 1
    integer, public, parameter :: lwp_steady_state     = 2
    integer, public, save :: lwp_method = lwp_non_steady_state

    integer, public, parameter :: fxwp_disabled = 1
    integer, public, parameter :: fxwp_use_fswp = 2
    integer, public, parameter :: fxwp_use_flwp = 3
    integer, public, parameter :: fxwp_use_fpaw = 4
    integer, public, save :: fxwp_method = fxwp_disabled

    ! Both R and PAR are inputs, do nothing
    integer, public, parameter :: r_par_use_inputs = 1
    ! Derived R from PAR
    integer, public, parameter :: r_par_derive_r   = 2
    ! Derive PAR from R
    integer, public, parameter :: r_par_derive_par = 3
    ! Derive PAR from Cloudfrac
    integer, public, parameter :: r_par_derive_cloudfrac = 4
    integer, public, save :: r_par_method = r_par_use_inputs

    ! Use supplied SGS/EGS
    integer, public, parameter :: sgs_egs_use_inputs = 1
    ! Use latitude function to calculate SGS/EGS
    integer, public, parameter :: sgs_egs_latitude   = 2
    ! Use thermal time to calculate all seasonal factors for wheat
    integer, public, parameter :: sgs_egs_tt         = 3
    integer, public, parameter :: sgs_egs_tt_mb      = 4
    integer, public, parameter :: sgs_egs_tt_md      = 5
    ! Use thermal time to calculate all seasonal factors for potato
    integer, public, parameter :: sgs_egs_tt_pot     = 6
    ! Use thermal time to calculate all seasonal factors for tomato
    integer, public, parameter :: sgs_egs_tt_tom     = 7
    integer, public, save :: sgs_egs_method = sgs_egs_use_inputs

    ! ustar methods
    integer, public, parameter :: ustar_calculate = 1
    integer, public, parameter :: ustar_input = 2
    integer, public, parameter :: ustar_i_input = 3
    integer, public, save :: ustar_method = ustar_calculate


end module Options
