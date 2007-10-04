# Search path for fortran files
vpath %.f90 ../F

# Default target
all: $(pymod)

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(f95) -c $<

$(pymod): dose_f.pyf $(common) $(others)
	python f2py.py -c --fcompiler=$(fcompiler) --compiler=$(compiler) dose_f.pyf $(common) $(others)
