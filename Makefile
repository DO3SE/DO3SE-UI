subdirs = F f2py-build
.PHONY: $(subdirs)

export common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
export others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o




all: dose dose_f.so




dose_f.pyf:
	python f2py.py -h $@ -m dose_f $(common:%.o=F/%.f90) $(others:%.o=F/%.f90)

f2py-build: dose_f.pyf
	mkdir -p $@
	cp f2py.py dose_f.pyf $@/
	cp f2py.Makefile $@/Makefile
	$(MAKE) -C $@

dose_f.so: f2py-build
	cp f2py-build/dose_f.so dose_f.so

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
	rm -f dose_f.so dose
