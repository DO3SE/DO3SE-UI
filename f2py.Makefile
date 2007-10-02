# Search path for fortran files
vpath %.f90 ../F

# Compiler
F = gfortran

# Default target
all: dose_f.so

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose_f.so: dose_f.pyf $(common) $(others)
	python f2py.py -c --fcompiler=gnu95 dose_f.pyf $(common) $(others)
