F = gfortran -std=f95 -fimplicit-none -Wall
FD = gfortran -std=f95 -fimplicit-none -Wall -g -ffpe-trap=zero,invalid,overflow,underflow

# Default target
all: dose

# Objects
include objects.mk

# Rule for building .o and .mod files
%.o %.mod: %.f90
ifeq ($(DEV),TRUE)
	# Compile with debugging
	$(FD) -c $<
else
	$(F) -c $<
endif

dose: $(objects) dose.o
	$(F) -o $@ $^

clean:
	rm -f *.o *.mod dose dose.exe
