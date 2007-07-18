program test_phen
    use Phenology_ml,  only : Init_phenology, Growing_season, Phenology
    use LandClasses_ml, only: landuse, NLANDUSE
    implicit none

    character(len=80) :: errmsg
    integer :: lu, ilat              ! Landuse and latitude index
    integer :: daynumber 
    integer, dimension(NLANDUSE) ::  SGS, EGS   
    integer, parameter  :: ionum = 50
    real :: latitude, LAI, SAI, hveg

    call Init_phenology(ionum,errmsg)

    if( errmsg /= "ok" ) then
        print *, "ERRMSG!! ", errmsg
        stop
     end if


    !do ilat = 40, 70, 10
    do ilat = 50, 50
      latitude = real(ilat)

        do lu = 1, 17 
            call Growing_season(lu,latitude,SGS(lu),EGS(lu))
        end do
    
    
        do daynumber = 100, 240, 20
    
          print *, "-----------"
          print *, "Latitude ", latitude, "Daynumber ", daynumber
          print "(a4,a4,2a4,a5,3a8,/)", "lu ", "code", "SGS", "EGS", &
                    "Jday", "LAI", "SAI", "hveg"
    
          !do lu = 5, 5  ! for temperate crops
          do lu = 1, 17
    
             call Phenology(daynumber,lu,SGS(lu),EGS(lu),LAI,SAI,hveg)
    
             print "(i4,a4,2i4,i5,3f8.3)", lu,landuse(lu)%code, SGS(lu), EGS(lu), &
                    daynumber, LAI, SAI, hveg
          end do
    
        end do ! daynumber loop
     end do ! ilat loop

end program test_phen
