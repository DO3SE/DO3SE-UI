#####################################################################
# DOSE model build system
#####################################################################

#####################################################################
# Compilers for different platforms
#####################################################################

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
# Platform is autodetected based on the output of the 'uname'
# command.  (Right now it is "Windows" or "something else".)
#####################################################################

# On Windows, the 'uname' command will give MINGW32_NT-x.x (because
# the only available uname is that from MinGW)
ifeq ($(shell sh -c 'uname -s | cut -c 1-7'),MINGW32)
	# Set the compilers
	export F=$(WIN32_F)
	export F95=$(WIN32_F95)
	export F2PY_COMPILER=$(WIN32_F2PY_COMPILER)
	export F2PY_FCOMPILER=$(WIN32_F2PY_FCOMPILER)
	# Set paths to compiled objects
	export DO3SE_BIN=dose.exe
	export PYMOD=do3se/do3se_fortran.pyd
else
	# Set the compilers
	export F=$(LINUX_F)
	export F95=$(LINUX_F95)
	export F2PY_COMPILER=$(LINUX_F2PY_COMPILER)
	export F2PY_FCOMPILER=$(LINUX_F2PY_FCOMPILER)
	# Set paths to compiled objects
	export DO3SE_BIN=dose
	export PYMOD=do3se/do3se_fortran.so
endif
    



subdirs = F f2py-build
.PHONY: $(subdirs)

export common = constants.o params_veg.o params_site.o inputs.o variables.o functions.o
export others = environmental.o evapotranspiration.o irradiance.o phenology.o r.o soil.o o3.o run.o


export DIST_SRC_DIR = DO3SE-src-$(shell date +"%Y%m%d")
export DIST_SRC_FILE = $(DIST_SRC_DIR).zip
export DIST_F_SRC_DIR = DO3SE-src-F-$(shell date +"%Y%m%d")
export DIST_F_SRC_FILE = $(DIST_F_SRC_DIR).zip
export DIST_UI_DIR = DO3SE-$(shell date +"%Y%m%d")
export DIST_UI_FILE = $(DIST_UI_DIR).zip


all: $(DO3SE_BIN)


py: $(PYMOD)


do3se_fortran.pyf:
	python f2py.py -h $@ -m do3se_fortran $(common:%.o=F/%.f90) $(others:%.o=F/%.f90)

f2py-build: do3se_fortran.pyf
	mkdir -p $@
	cp f2py.py do3se_fortran.pyf $@/
	cp f2py.Makefile $@/Makefile
	$(MAKE) -C $@

$(PYMOD): f2py-build
	cp f2py-build/`basename $@` $@

clean_do3se_fortran:
	rm -rf f2py-build do3se_fortran.pyf

F:
	$(MAKE) -C $@

$(DO3SE_BIN): F
	mv F/$@ $@


clean_dose:
	$(MAKE) -C F clean

clean: clean_do3se_fortran clean_dose


clean_all: clean
	rm -f $(PYMOD) $(DO3SE_BIN)
	

#####################################################################
# Rules for building distribution packages
#####################################################################

dist-src-win: clean_all
	rm -rf $(DIST_SRC_DIR) $(DIST_SRC_FILE)
	mkdir -p $(DIST_SRC_DIR)
	cp -a F/ do3se/ run-do3se.py f2py.Makefile f2py.py Makefile setup.py $(DIST_SRC_DIR)
	todos $(DIST_SRC_DIR)/F/*.f90
	zip -r $(DIST_SRC_FILE) $(DIST_SRC_DIR)
	rm -rf $(DIST_SRC_DIR)

dist-f-src-win: clean_all
	rm -rf $(DIST_F_SRC_DIR) $(DIST_F_SRC_FILE)
	mkdir -p $(DIST_F_SRC_DIR)
	cp -a F/ Makefile $(DIST_F_SRC_DIR)
	todos $(DIST_F_SRC_DIR)/F/*.f90
	zip -r $(DIST_F_SRC_FILE) $(DIST_F_SRC_DIR)
	rm -rf $(DIST_F_SRC_DIR)

dist-ui-win:
	rm -rf $(DIST_UI_DIR) $(DIST_UI_FILE)
	python setup.py py2exe -d $(DIST_UI_DIR)
	zip -r $(DIST_UI_FILE) $(DIST_UI_DIR)
	rm -rf $(DIST_UI_DIR)
