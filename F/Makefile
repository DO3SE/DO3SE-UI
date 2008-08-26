# Compiler
F = g95 -std=F

# Default target
all: dose

# Objects
common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose: $(others) dose.o
	$(F) -o $@ $(common) $(others) dose.o

clean:
	rm -f *.o *.mod dose
