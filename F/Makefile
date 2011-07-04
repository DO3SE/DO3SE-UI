F = g95 -std=F

# Default target
all: dose

# Objects
include objects.mk

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

dose: $(objects) dose.o
	$(F) -o $@ $^

clean:
	rm -f *.o *.mod dose dose.exe
