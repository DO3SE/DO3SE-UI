subdirs = F f2py-build
.PHONY: $(subdirs)

export common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
export others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

targetmachine = $(shell gcc -dumpmachine)

ifeq ($(targetmachine),mingw32)
	f95 = g95
	fcompiler = g95
	compiler = mingw32
	pymod = dose_f.pyd
else
	f95 = gfortran
	fcompiler = gnu95
	compiler = unix
	pymod = dose_f.so
endif

export f95
export fcompiler
export compiler
export pymod


all: dose


py: $(pymod)


dose_f.pyf:
	python f2py.py -h $@ -m dose_f $(common:%.o=F/%.f90) $(others:%.o=F/%.f90)

f2py-build: dose_f.pyf
	mkdir -p $@
	cp f2py.py dose_f.pyf $@/
	cp f2py.Makefile $@/Makefile
	$(MAKE) -C $@

$(pymod): f2py-build
	cp f2py-build/$@ $@

clean_dose_f:
	rm -rf f2py-build dose_f.pyf


F:
	$(MAKE) -C $@

dose: F
	cp F/$@ $@

clean_dose:
	$(MAKE) -C F clean

clean: clean_dose_f clean_dose


clean_all: clean
	rm -f $(pymod) dose
