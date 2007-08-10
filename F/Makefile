FORTRAN		= gfortran

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(FORTRAN) -c $<

# Modules needed by all of the higher level modules
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o

# Higher level modules
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3_effects.o o3_flux.o run.o test.o

# Set up the module dependancy
$(others): $(common)

do3se: $(common) $(others)
	$(FORTRAN) -o $@ $(common) $(others)

do3se_old:
	$(FORTRAN) -o $@ Baum_DOSE_test.f90

test: do3se do3se_old
	./do3se_old > TEST_OUTPUT_old
	./do3se > TEST_OUTPUT_new
	diff -u -s TEST_OUTPUT_old TEST_OUTPUT_new

ntest: do3se do3se_old
	./do3se_old > TEST_OUTPUT_old
	./do3se > TEST_OUTPUT_new
	ndiff --relative-error 1.0e-6 TEST_OUTPUT_old TEST_OUTPUT_new

clean:
	rm -f $(common) $(others) $(subst .o,.mod,$(common) $(others))

clean_test:
	rm -f TEST_OUTPUT_old TEST_OUTPUT_new
