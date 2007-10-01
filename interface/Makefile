.PHONY: dose_fortran_src

all: dose_fortran.so

dose_fortran_src:
	mkdir -p $@
	cp dose_fortran.pyf f2py.py $@/
	cp F.Makefile $@/Makefile
	$(MAKE) -C $@

dose_fortran.so: dose_fortran_src
	cp $</$@ $@

clean:
	rm -rf dose_fortran_src

clean_all: clean
	rm dose_fortran.so
