program Run_DOSE
    use Switchboard
    use Run

    sai_method = sai_equals_lai
    rn_method = rn_calculate
    leaf_fphen_method = leaf_fphen_equals_fphen
    ra_method = ra_simple
    fo3_method = fo3_disabled
    fxwp_method = fxwp_disabled
    r_par_method = r_par_use_inputs

    call Run_With_Files("input_newstyle.csv", "output.csv")
end program Run_DOSE

