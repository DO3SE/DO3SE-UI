#####################################################################
# DOSE model build system
#####################################################################

#####################################################################
# Set paths and compilers
#####################################################################

# Build system paths for Windows
WIN32_LIB_MINGW = /c/mingw/lib
WIN32_BIN_MINGW = /c/mingw/bin
WIN32_BIN_MSYS  = /c/msys/1.0/bin

# Compiler commands for Windows
WIN32_F                 = g95 -std=F
WIN32_F95               = g95
WIN32_F2PY_COMPILER     = mingw32
WIN32_F2PY_FCOMPILER    = g95

# Compiler commands for Linux
LINUX_F                 = g95 -std=F
LINUX_F95               = gfortran -fPIC
LINUX_F2PY_COMPILER     = unix
LINUX_F2PY_FCOMPILER    = gnu95

#####################################################################
# Set build system variables depending on the platform.
# 
# Currently supported platforms are "linux" and "win32", with the
# default being "linux".  Run "make PLATFORM=win32" to build for
# Windows.
#####################################################################

# Default to "linux" if no platform is set
ifndef PLATFORM
	PLATFORM=linux
endif
export PLATFORM

ifeq ($(PLATFORM),win32)
	# Modify environment variables so the user doesn't need to
	export LIBRARY_PATH := $(WIN32_LIB_MINGW):$(LIBRARY_PATH)
	export PATH := $(WIN32_BIN_MINGW):$(WIN32_BIN_MSYS):$(PATH)
	# Set the compilers
	export F=$(WIN32_F)
	export F95=$(WIN32_F95)
	export F2PY_COMPILER=$(WIN32_F2PY_COMPILER)
	export F2PY_FCOMPILER=$(WIN32_F2PY_FCOMPILER)
	# Set the python module path
	export PYMOD=ui/dose_f.pyd
else
	# Set the compilers
	export F=$(LINUX_F)
	export F95=$(LINUX_F95)
	export F2PY_COMPILER=$(LINUX_F2PY_COMPILER)
	export F2PY_FCOMPILER=$(LINUX_F2PY_FCOMPILER)
	# Set the python module path
	export PYMOD=ui/dose_f.so
endif
    



subdirs = F f2py-build
.PHONY: $(subdirs)

export common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
export others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o

date = $(shell date +"%Y%m%d")


all: dose


py: $(PYMOD)


dose_f.pyf:
	python f2py.py -h $@ -m dose_f $(common:%.o=F/%.f90) $(others:%.o=F/%.f90)

f2py-build: dose_f.pyf
	mkdir -p $@
	cp f2py.py dose_f.pyf $@/
	cp f2py.Makefile $@/Makefile
	$(MAKE) -C $@

$(PYMOD): f2py-build
	cp f2py-build/`basename $@` $@

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
	rm -f $(PYMOD) dose
	

#####################################################################
# Rules for building distribution packages
#####################################################################
	
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
