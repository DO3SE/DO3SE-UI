FORTRAN		= gfortran -fdefault-real-8
F2PY		= f2py
F2PY_BUILD 	= f2py --f77exec=$(FORTRAN) --f90exec=$(FORTRAN)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(FORTRAN) -c $<

# Modules needed by all of the higher level modules
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o

# Higher level modules
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3_effects.o o3_flux.o Run.o

# Set up the module dependancy
$(others): $(common)

%.pyf: %.f90
	$(F2PY) $< -m $(subst .f90,,$<) -h $@

%.so: %.o $(common)
	$(F2PY_BUILD) -c `echo $< | cut -d '.' -f -1`.pyf $< $(subst $<,,$(common))


do3se.pyf: $(common) $(others)
	$(F2PY) -m do3se $(subst .o,.f90,$(common) $(others)) -h $@

do3se.so: $(common) $(others)
	$(F2PY_BUILD) -c do3se.pyf $(common) $(others)

do3se: $(common) $(others) Test.o
	$(FORTRAN) -o do3se $(common) $(others) Test.o

do3se2:
	$(FORTRAN) -o do3se2 $(subst .o,.f90,$(common) $(others)) Test.f90

clean:
	rm -f *.o
	rm -f *.mod

clean_all: clean
	rm -f *.so
