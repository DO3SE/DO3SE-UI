# Compiler
F = F

# Object files
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

# Default target
all: dose

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose: $(others) test.o
	$(F) -o $@ $(common) $(others) test.o

clean:
	rm -f *.o *.mod dose dose_fortran.pyf

dose_fortran.pyf:
	python ../interface/f2py.py -m dose_fortran -h $@ $(common:.o=.f90) $(others:.o=.f90)
