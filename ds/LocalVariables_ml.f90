module LocalVariables_ml

! Meteorological variables for local area, e.g. for a measurement site
! or for a specific landuse within a grid square

    real, public, save ::  &
        Ts_C         &      ! Surface temperature in degrees C
       ,psurf        &      ! Surface pressure, Pa
       ,precip       &      ! Precipitation at ground, mm/hr
       ,wetarea      &      ! Area (fraction) of grid square assumed wet
       ,rh           &      ! Relative humidity, fraction (0-1)
       ,vpd          &      ! Vapour pressure deficit  (kPa) ! CHECK UNITS
       ,SWP          &      ! SWP  ! CHECK UNITS
       ,cl           &      ! Cloud-cover
!
! Micro-met
       ,ustar        &      ! friction velocity, m/s
       ,invL         &      ! 1/L, where L is Obukhiov length (1/m)
! Vegetation
       ,LAI          &      ! Leaf area index (m2/m2)
       ,SAI          &      ! Surface area index (m2/m2)
       ,hveg         &      ! Height of veg.      (m)
       ,d            &      ! displacement height (m)
       ,z0           &      ! roughness length    (m)
!
! Radiation
       ,PARsun       &      ! photosynthetic active radn. for sun-leaves
       ,PARshade     &      !  " " for shade leaves
       ,LAIsunfrac   &      ! fraction of LAI in sun
!
! Chemistry  
       ,so2nh3ratio         !  for CEH deposition scheme

   logical, public, save :: &
       is_wet              !  true if precip > 0

   integer, public, save :: snow      ! 1=snow present, 0 = no snow

end module LocalVariables_ml
