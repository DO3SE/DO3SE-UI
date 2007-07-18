PROG =	Test_Rsur

SRCS =	CEH_ml.f90 Functions_ml.f90 Gsto_ml.f90 Io_ml.f90 LandClasses_ml.f90 \
	LocalVariables_ml.f90 My_DryDep_ml.f90 Phenology_ml.f90 \
	PhysicalConstants_ml.f90 Radiation_ml.f90 Rb_ml.f90 Rsurface_ml.f90 \
	Test_Rsur.f90 Wesely_ml.f90

OBJS =	CEH_ml.o Functions_ml.o Gsto_ml.o Io_ml.o LandClasses_ml.o \
	LocalVariables_ml.o My_DryDep_ml.o Phenology_ml.o \
	PhysicalConstants_ml.o Radiation_ml.o Rb_ml.o Rsurface_ml.o \
	Test_Rsur.o Wesely_ml.o

LIBS =	

CC = cc
CFLAGS = -O
FC = f77
FFLAGS = -O
F90 = f90
F90 = F
F90FLAGS = -g -Rb -Rc
F90FLAGS = -g -gline
LDFLAGS = -s

all: $(PROG)

$(PROG): $(OBJS)
	$(F90) $(LDFLAGS) -o $@ $(OBJS) $(LIBS)

clean:
	rm -f $(PROG) $(OBJS) *.mod

.SUFFIXES: $(SUFFIXES) .f90

.f90.o:
	$(F90) $(F90FLAGS) -c $<

Gsto_ml.o: LandClasses_ml.o LocalVariables_ml.o
My_DryDep_ml.o: Wesely_ml.o
Phenology_ml.o: Functions_ml.o LandClasses_ml.o
Radiation_ml.o: PhysicalConstants_ml.o
Rb_ml.o: LocalVariables_ml.o My_DryDep_ml.o PhysicalConstants_ml.o \
	Wesely_ml.o
Rsurface_ml.o: CEH_ml.o Gsto_ml.o LandClasses_ml.o LocalVariables_ml.o \
	My_DryDep_ml.o Wesely_ml.o
Test_Rsur.o: Gsto_ml.o LandClasses_ml.o LocalVariables_ml.o My_DryDep_ml.o \
	Phenology_ml.o Radiation_ml.o Rb_ml.o Rsurface_ml.o
