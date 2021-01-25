program Run_DOSE
    use Switchboard
    use Run
    CHARACTER(len=255) :: homedir
    CHARACTER(len=255) :: input_path
    CHARACTER(len=255) :: output_path

    sai_method = sai_equals_lai
    rn_method = rn_calculate
    leaf_fphen_method = leaf_fphen_equals_fphen
    ra_method = ra_simple
    fo3_method = fo3_disabled
    fswp_method = fswp_exponential
    lwp_method = lwp_non_steady_state
    fxwp_method = fxwp_disabled
    r_par_method = r_par_use_inputs
    sgs_egs_method = sgs_egs_use_inputs

    homedir = "tests/spanish_wheat_DO3SE_3_1/"
    input_path = trim(homedir) // "input.csv"
    output_path = trim(homedir) // "output3.csv"
    ! call Run_With_Files("inputb.csv", "output.csv")
    call Run_With_Files(input_path, output_path)
end program Run_DOSE

