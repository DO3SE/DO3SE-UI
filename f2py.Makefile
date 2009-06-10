# Search path for fortran files
vpath %.f90 ../F

# Default target
all: $(PYMOD)

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F95) -c $<

$(PYMOD): dose_f.pyf $(common) $(others)
	python f2py.py -c --fcompiler=$(F2PY_FCOMPILER) --compiler=$(F2PY_COMPILER) dose_f.pyf $(common) $(others)
