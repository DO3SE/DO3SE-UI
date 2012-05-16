F = gfortran -std=f95 -fimplicit-none -Wall

DO3SE_EXEC = dose
DO3SE_STATICLIB = do3se.a

# Default target
all: $(DO3SE_EXEC)

staticlib: $(DO3SE_STATICLIB)

# Objects
include objects.mk

# Rule for building .o and .mod files
%.o %.mod: %.f90
	$(F) -c $<

$(DO3SE_EXEC): $(DO3SE_STATICLIB) dose.o
	$(F) -o $@ dose.o $(DO3SE_STATICLIB)

$(DO3SE_STATICLIB): $(objects)
	rm -f $@
	ar cq $@ $^

clean:
	rm -f *.o *.mod
	rm -f $(DO3SE_EXEC) $(DO3SE_EXEC).exe
	rm -f $(DO3SE_STATICLIB)
