# Search path for fortran files
vpath %.f90 ../../F

# Compiler
F = gfortran

# Object files
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

# Default target
all: dose_fortran.so

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose_fortran.so: $(others)
	python f2py.py -c --fcompiler=gnu95 dose_fortran.pyf $(common) $(others)
