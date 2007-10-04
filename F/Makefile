# Compiler
F = F

# Default target
all: dose

# Dependancy heirarchy
$(others): $(common)

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose: $(others) dose.o
	$(F) -o $@ $(common) $(others) dose.o

clean:
	rm -f *.o *.mod dose
