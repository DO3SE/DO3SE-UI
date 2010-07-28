# Default target
all: $(DO3SE_BIN)

# Objects
include objects.mk

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

$(DO3SE_BIN): $(objects) dose.o
	$(F) -o $@ $^

clean:
	rm -f *.o *.mod $(DO3SE_BIN)
