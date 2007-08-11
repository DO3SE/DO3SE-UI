FORTRAN		= gfortran
F2PY		= f2py
F2PY_BUILD 	= f2py --f77exec=$(FORTRAN) --f90exec=$(FORTRAN)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(FORTRAN) -c $<

# Modules needed by all of the higher level modules
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o

# Higher level modules
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3_effects.o o3_flux.o run.o

# Set up the module dependancy
$(others): $(common)

do3se.pyf: $(common) $(others)
	$(F2PY) -m do3se $(subst .o,.f90,$(common) $(others)) -h $@

do3se.so: $(common) $(others)
	$(F2PY_BUILD) -c do3se.pyf $(common) $(others)

do3se: $(common) $(others) test.o
	$(FORTRAN) -o $@ $(common) $(others) test.o

do3se_old:
	$(FORTRAN) -o $@ Baum_DOSE_test.f90

clean:
	rm -f $(common) $(others) $(subst .o,.mod,$(common) $(others))

clean_all: clean
	rm -f do3se.so do3se do3se_old
