# Solar Radiation

There are multiple methods for defining solar radiation in the DO3SE model.

- Both R and PAR are inputs, do nothing
- Derived R from PAR
- Derive PAR from R
- Derive PAR from Cloudfrac

The choice of method is decided based on the inputs provided.

```python
# Handle PAR/Global radiation input/derivation
if 'par' in input_fields and 'r' in input_fields:
  # - Both R and PAR are inputs, do nothing
    self.options['r_par_method'] = model.options.r_par_use_inputs
    _log.debug('R/PAR calculation: use inputs')
elif 'par' in input_fields:
# - Derived R from PAR
    self.options['r_par_method'] = model.options.r_par_derive_r
    _log.debug('R/PAR calculation: derive R')
elif 'r' in input_fields:
# - Derive PAR from R
    self.options['r_par_method'] = model.options.r_par_derive_par
    _log.debug('R/PAR calculation: derive PAR')
elif 'cloudfrac' in input_fields:
# - Derive PAR from Cloudfrac
    self.options['r_par_method'] = model.options.r_par_derive_cloudfrac
    _log.debug('R/PAR calculation: derive PAR from cloudfrac')
else:
    raise RequiredFieldError(['par', 'r'])
```

