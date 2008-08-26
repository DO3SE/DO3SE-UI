subdirs = F f2py-build
.PHONY: $(subdirs)

export common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
export others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

targetmachine = $(shell gcc -dumpmachine)
date = $(shell date +"%Y%m%d")

ifeq ($(targetmachine),mingw32)
	f95 = g95
	fcompiler = g95
	compiler = mingw32
	pymod = ui/dose_f.pyd
else
	f95 = gfortran -fPIC
	fcompiler = gnu95
	compiler = unix
	pymod = ui/dose_f.so
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
	cp f2py-build/`basename $@` $@

clean_dose_f:
	rm -rf f2py-build dose_f.pyf


F:
	$(MAKE) -C $@

dose: F
	cp F/$@ $@

dist-f-win:
	mkdir -p dose-f-$(date)
	cp F/*.f90 dose-f-$(date)/
	cp F/Makefile dose-f-$(date)/
	todos dose-f-$(date)/*
	zip -r dose-f-$(date).zip dose-f-$(date)
	rm -r dose-f-$(date)

dist-ui-win:
	rm -f dose-ui-$(date).zip
	python setup.py py2exe -d dose-ui-$(date)
	python fix-dlls.py dose-ui-$(date)
	zip -r dose-ui-$(date).zip dose-ui-$(date)
	rm -r dose-ui-$(date)

clean_dose:
	$(MAKE) -C F clean

clean: clean_dose_f clean_dose


clean_all: clean
	rm -f $(pymod) dose
