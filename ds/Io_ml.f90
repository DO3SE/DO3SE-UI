module Io_ml

!_____________________________________________________________________________
! -- provides routines to check/open files
!_____________________________________________________________________________
implicit none

! -- subroutines in this module:

public :: check_file   !  checks that file exists and stops if required
public :: open_readfile    !  checks that file exists and opens if required
public :: open_writefile    !  checks that file exists and opens if required
public :: wordsplit    !  Splits input text into words

logical, public :: fexist                      ! true if file exists 
integer, public, parameter :: NO_FILE = 777    ! code for non-existing file
integer, public, save :: ios                   ! i/o error status number
character(len=120), public :: io_msg           ! i/o error message

contains

!===========================================================>

subroutine check_file(fname,needed,logio)
  !**************************************************************
  ! Checks for the existence of a file. If the file is
  ! specified as "needed", and missing, an error message is
  ! printed and the run is stopped.

  character (len=*),   intent(in)  :: fname    ! file name
  logical,             intent(in)  :: needed   ! see below
  integer,             intent(in)  :: logio    ! i/o num to write messages
  
  io_msg = "ok"

  inquire(file=fname,exist=fexist)

  !write(unit=logio,fmt=*) "check_file::: ", fname
  if ( .not. fexist .and. .not. needed ) then
     write(unit=logio,fmt=*) "not needed ", fname, " ..skipping....."

  else if ( .not. fexist .and. needed ) then
     io_msg = "ERROR: Missing!!! in check-file:" // fname
     print *, io_msg
     write(unit=logio,fmt="(a)") io_msg

  else
     write(unit=logio,fmt=*) "Check-OK. File exists" // fname
  end if
end subroutine check_file

!===========================================================>

subroutine open_readfile(io_num,logio,fname,needed,skip)
  !**************************************************************
  ! Checks for the existence of a file and opens if present. If the 
  ! file is specified as "needed", and missing, an error message is
  ! printed and the run is stopped.

  integer,             intent(in)  :: io_num   ! i/o number
  integer,             intent(in)  :: logio    ! i/o num to write messages
  character (len=*),   intent(in)  :: fname    ! file name
  logical, optional,   intent(in)  :: needed   ! see below
  integer, optional,   intent(in)  :: skip     ! no. of text lines to be 
                                               ! skipped
  character(len=120) :: txt                    ! Used for skipped text


  integer :: i  ! local loop counter

  io_msg = "ok"  ! start with  assumed OK status

  if ( needed ) then 
      call check_file(fname,needed,logio)
      if ( io_msg /= "ok" ) then
          return
      end if
  end if

  write(unit=logio,fmt=*) "Opening new file ", io_num, fname
  open(unit=io_num,file=fname,status="old",&
                      action="read",position="rewind",iostat=ios)
  if ( ios /= 0 ) then
     io_msg = "Open error " // fname
     write(unit=logio,fmt=*)  io_msg
     return
  end if

  if (present(skip)) then ! Read (skip) some lines at start of file
      do i = 1, skip
           read(unit=io_num,fmt="(a120)") txt
      end do
  end if ! skip

end subroutine open_readfile

!===========================================================>

subroutine open_writefile(io_num,logio,fname)
  !**************************************************************

  integer,             intent(in)  :: io_num   ! i/o number
  integer,             intent(in)  :: logio    ! i/o number for messages
  character (len=*),   intent(in)  :: fname    ! file name

  ios = 0   ! start with  assumed OK status
  io_msg = "ok"

  open(unit=io_num,file=fname,status="old",action="write",iostat=ios)
  if( ios /= 0 ) then
     io_msg = "File-write-open Error! " // fname
     write(unit=logio,fmt=*)  io_msg
     return
  end if

end subroutine open_writefile

!===========================================================>

subroutine wordsplit(text,nword_max,wordarray,nwords,errcode)
  !**************************************************************
  !   Subroutine takes in a character string and splits it into
  !   a word-array, of length nwords        
  !**************************************************************

 !-- arguments
  character(len=*), intent(in) ::  text       ! to be split
  integer,          intent(in) ::  nword_max  ! max. no. words expected

  character(len=*), dimension(:), intent(out) :: wordarray
  integer,          intent(out) :: nwords      ! no. words found
  integer,          intent(out) :: errcode      ! no. words found

  !-- local
  logical   :: wasinword   ! true if we are in or have just left a word
  integer   :: i, is, iw
  character(len=1) ::  c

  errcode = 0
  is = 0 ! string index
  iw = 1 ! word index
  wordarray(1) = ""

  do i = 1, len_trim(text)
      c = text(i:i)
      if( c /= " " ) then
          is = is + 1
          wordarray(iw)(is:is) = c
          wasinword = .true.
      else 
         if ( wasinword ) then
             iw = iw + 1
             wordarray(iw) = ""
             wasinword = .false.
             is = 0
         end if
      end if
  end do

  nwords = iw
  if (  nwords >= nword_max ) then
      errcode = 2
      print *, "ERROR in WORDSPLIT : Problem at ", text
      print *,"Too many words"
  end if

 end subroutine wordsplit
end module Io_ml
