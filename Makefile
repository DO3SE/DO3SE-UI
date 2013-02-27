#####################################################################
# DOSE model build system
#####################################################################

export DIST_SRC_DIR = DO3SE-src-$(shell date +"%Y%m%d")
export DIST_SRC_FILE = $(DIST_SRC_DIR).zip
export DIST_F_SRC_DIR = DO3SE-src-F-$(shell date +"%Y%m%d")
export DIST_F_SRC_FILE = $(DIST_F_SRC_DIR).zip

.PHONY: doc


all:
	# 'make dose' for standalone model, or 'make py_ext' for Python extension for UI

py_ext:
	python2 setup.py build_ext
	# Suppress errors, because there will be no .pyd on Linux or .so on Windows
	cp build/lib.*/do3se/*.so build/lib.*/do3se/*.pyd do3se/ 2> /dev/null ; exit 0

clean_py_ext:
	rm -f do3se/*.so do3se/*.pyd *.pyf

dose:
	$(MAKE) -C F
	cp F/$@ $@

clean_dose:
	$(MAKE) -C F clean
	rm -f dose dose.exe

doc:
	$(MAKE) -C doc/dev html

clean_doc:
	$(MAKE) -C doc/dev clean

clean: clean_dose clean_py_ext


#####################################################################
# Rules for building distribution packages
#####################################################################

dist-src-win: clean
	rm -rf $(DIST_SRC_DIR) $(DIST_SRC_FILE)
	mkdir -p $(DIST_SRC_DIR)
	cp -a F/ do3se/ *.py Makefile $(DIST_SRC_DIR)
	todos $(DIST_SRC_DIR)/F/*.f90
	zip -r $(DIST_SRC_FILE) $(DIST_SRC_DIR)
	rm -rf $(DIST_SRC_DIR)

dist-f-src-win: clean
	rm -rf $(DIST_F_SRC_DIR) $(DIST_F_SRC_FILE)
	mkdir -p $(DIST_F_SRC_DIR)
	cp -a F/*.f90 F/Makefile F/objects.mk $(DIST_F_SRC_DIR)
	todos $(DIST_F_SRC_DIR)/*.f90
	zip -r $(DIST_F_SRC_FILE) $(DIST_F_SRC_DIR)
	rm -rf $(DIST_F_SRC_DIR)
