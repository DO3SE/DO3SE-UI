# Compilers
export F = F
export F95 = gfortran

subdirs = F

.PHONY: $(subdirs)

$(subdirs):
	$(MAKE) -C $@

dose: F
	cp F/dose dose
