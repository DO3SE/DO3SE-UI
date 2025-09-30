# Resistance model

There are 2 Ra methods in the DO3SE model

1. Simple
2. Heat flux

### Simple

Set the following parameters:

```
  "ra_method": "simple",
```

```fortran
  real, intent(in) :: ustar   ! Friction velocity (m/s)
  real, intent(in) :: z1      ! Lower height (m)
  real, intent(in) :: z2      ! Upper height (m)
  real, intent(in) :: d       ! Zero displacement height (m)

  real :: ra                  ! Output: aerodynamic resistance (s/m)

  real, parameter :: K = 0.41 ! von Karman's constant
  ra = (1.0 / (ustar * K)) * log((z2 - d) / (z1 - d))
```

### Heat flux

```fortran
  real, intent(in) :: ustar   ! Friction velocity (m/s)
  real, intent(in) :: z1      ! Lower height (m)
  real, intent(in) :: z2      ! Upper height (m)
  real, intent(in) :: invL    ! Inverse Monik length

  real :: ra                  ! Output: aerodynamic resistance (s/m)

  real, parameter :: K = 0.41 ! von Karman's constant

  Ra = log(z2/z1) - calc_PsiH(z2*invL) + calc_PsiH(z1*invL)
  Ra = Ra/(k*ustar)
```

The heat flux method requires the following additional inputs

- Hd - Sensible heat flux (W/m^2)
- ustar_ref input - Ustar at reference height

Set the following parameters:

```
    "input_fields": [
    ...
      "ustar_ref",
      "hd",
    ...
  ],
  "ra_method": "heat_flux",

```
## Setting Vegitation heights

The do3se model can transfer ozone from a reference canopy to a target canopy.

The following parameters are important for this:
```fortran
  ! Modelled Heights
  real, public, save :: h = 25            ! Canopy height (m)
  real, public, save :: zo                ! Roughness length (m)
  real, public, save :: d                 ! Displacement height (m)

  ! Measurement heights
  real, public, save :: uzR = 25      ! Windspeed measurement height (m)
  real, public, save :: O3zR = 25     ! Ozone concentration measurement height (m)

  ! Properties of vegetation over which windspeed is measured
  real, public, save :: u_h = 25      ! Canopy height (m)
  real, public, save :: u_d           ! Canopy displacement height (m)
  real, public, save :: u_zo          ! Canopy roughness length

  ! Properties of vegetation over which O3 concentration is measured
  real, public, save :: O3_h = 25     ! Canopy height (m)
  real, public, save :: O3_d          ! Canopy displacement height (m)
  real, public, save :: O3_zo         ! Canopy roughness length
```

The reference canopy is generally the canopy state associated with the met input data. I.e. if met data was recorded in a field of grass with measurements taken 1m above the ground level then `u_h` and `O3_h` would be the height of the grass and `uzR` and `O3zR` would be 1m.

The target canopy is the canopy that the do3se model is simulating. I.e if the model is simulating a tree canopy with height 20m then `h` would be 20.

![Tool DO3SE](end_user/tool-do3se.jpg)
