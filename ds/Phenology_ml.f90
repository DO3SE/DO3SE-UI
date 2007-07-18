module Phenology_ml

  !/*** DESCRIPTION**********************************************************
  !/   reads in or sets phenology data used for the default deposition module
  !/   Users with own phenology data can simply provide their own subroutines
  !/   (replacing Init_phenology and Phenology)
  !/   Most of these data are for test purposes only, for example, in respect 
  !/   of growing seasons.
  !/*************************************************************************

  use LandClasses_ml, only: NLANDUSE, landuse    ! No.land-classes and params
  use Functions_ml,   only: Polygon

  implicit none
  private


  public  :: Init_phenology    ! Reads in data used in UK deposition modules
  public  :: Phenology         ! Sets LAI, SAI, hveg
  public  :: Growing_season 

  real, private, parameter :: STUBBLE  = 0.01 ! Veg. ht. out of season

 !/*****   Data to be read from Phenology_inputs.dat:

  type, private :: phenol
     character(len=3) :: code
     real    ::  hveg_max
     real    ::  rootdepth
     integer ::  SGS50        ! Start of grow season at 50 deg. N
     integer ::  DSGS         ! Increase in SGS per degree N
     integer ::  EGS50        ! End of grow season at 50 deg. N
     integer ::  DEGS         ! Increase in EGS per degree N
     real    ::  LAImin       ! Min value of LAI
     real    ::  LAImax       ! Max value of LAI
     integer ::  SLAIlen, ELAIlen   ! Lengths of LAI growth/decline periods
  end type phenol

  type(phenol), private, dimension(NLANDUSE) :: Phen
  logical, private, parameter :: MY_DEBUG = .true.    ! helps with extra printouts

contains

!=======================================================================
  subroutine Init_phenology(ionum,errmsg)
!=======================================================================
!   Reads in data associated with UK deposition phenology

  integer, intent(in)             :: ionum    ! i/o number
  character(len=*), intent(inout) ::  errmsg
  integer :: lu      ! landuse category index
  integer :: ios     ! file-open status
  character(len=80) ::  header

 ! read in phenology-associated data (LAI, etc.)
  
      errmsg = "ok"    ! okay so far....
      open(unit=ionum,file="Phenology_inputs.dat",status="old",&
           position="rewind",action="read",iostat=ios)

      if ( ios /= 0 ) then
           errmsg = "Error in open, not " // errmsg 
           return
      end if

      do lu = 1, 5      ! just read and skip headers first
         read(unit=ionum,fmt="(a)",iostat=ios) header
         if( MY_DEBUG ) print *, header
         if ( ios /= 0 ) errmsg = "Error in headers, not " // errmsg 
      end do


      do lu = 1, NLANDUSE
         read(unit=ionum,fmt=*,iostat=ios)  Phen(lu) !tmpline 
         if( MY_DEBUG) print "(a4,2f6.1,4i6,2f7.2,2i6)", Phen(lu)

         if ( ios /= 0 ) then
           errmsg = "Error in read!, not " // Phen(lu)%code // errmsg 
           return
         end if
         if ( Phen(lu)%code /= landuse(lu)%code ) then
           errmsg = "Mis-match!! " // Phen(lu)%code // landuse(lu)%code
           return
         end if
      end do 
      if( MY_DEBUG ) print *, header    ! Should be a line, just for decoration...
      close(unit=ionum)

  end subroutine Init_phenology

!=======================================================================
    subroutine Growing_season(lu,lat,SGS,EGS)
!=======================================================================

!   calculates the start and end of growing season for land-use
!   class "lu" and latitude "lat".  
!

    integer, intent(in) :: lu         ! Land-use index
    real,    intent(in) :: lat        ! Latitude 
    integer, intent(out) :: SGS, EGS  ! start and end of growing season

  !/ plus SGS50, DSG50 from  module DepVariables_ml

      if ( Phen(lu)%DSGS > 0 )  then ! calculate

        SGS = int ( 0.5 +  Phen(lu)%SGS50 + Phen(lu)%DSGS * (lat-50.0) )
        EGS = int ( 0.5 +  Phen(lu)%EGS50 + Phen(lu)%DEGS * (lat-50.0) )
      else
        SGS = Phen(lu)%SGS50
        EGS = Phen(lu)%EGS50
      end if

      EGS = min(EGS, 366 )  ! Keeps EGS to 366 to allow for leap year
                            ! (and ignore diff 365/366 otherwise)

  end subroutine Growing_season

  !=======================================================================
  subroutine Phenology(daynumber,lu,SGS,EGS,LAI,SAI,hveg)
  !=======================================================================
  ! calculates 1) LAI  leaf area index (1 sided, m2/m2)
  !            2) SAI  surface area index
  !            3) hveg vegetayion height

    integer, intent(in)  :: daynumber, lu, SGS, EGS
    real   , intent(out) :: LAI, SAI, hveg

      !+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      ! 1) LAI:

        if ( landuse(lu)%Gcalc ) then    ! Growing veg. present

            LAI =  Polygon(daynumber, 0.0, Phen(lu)%LAImin,Phen(lu)%LAImax, &
                      SGS, Phen(lu)%SLAIlen, EGS, Phen(lu)%ELAIlen )

        else 
           LAI = 0.0

        end if

      !+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      ! 2) SAI:    Surface area vegetation assumed >= LAI for tall vegetation
      !           to account for bare branches and trunk.

          SAI = LAI

          if ( landuse(lu)%forest ) then
              SAI = LAI + 1.0     ! Addition to LAI to get surface area

          else if( landuse(lu)%code == "FWH" ) then
               SAI = LAI + 1.5   ! Artificial wheat - careful!!!!

          else if( landuse(lu)%crops ) then

               if ( daynumber < (SGS + Phen(lu)%SLAIlen) ) then
                     SAI = 5.0/3.5  * LAI
                else if ( daynumber <= EGS ) then
                     SAI = LAI + 1.5   ! Sensescent
                end if
          end if

      !+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
      ! 3) hveg: calculates vegetation height, m

            hveg = Phen(lu)%hveg_max   ! default

            if ( landuse(lu)%crops  )  then
                 !/ Allow height to change with LAI for crops
    
                 if ( daynumber < SGS .or. daynumber > EGS ) then  
    
                     hveg = STUBBLE
    
                 else if ( daynumber < SGS+Phen(lu)%SLAIlen ) then

                     hveg = Phen(lu)%hveg_max * LAI/Phen(lu)%LAImax
                     hveg = max(hveg,STUBBLE)

                 !/ else ... default applies, hveg_max
                 end if
             end if

  end subroutine Phenology

! =====================================================================
end module Phenology_ml
