# 
# FujiNet Config Loader Makefile
#
# 2021 apc.atari@gmail.com
#

.PHONY: all dist tools clean cleantools cleanall

DENSITY := SD
ifeq ($(DENSITY), DD)
	DENSITYOPT := -D
else
	DENSITYOPT := -S
endif

ifdef CONFIG_PROG
CONFIG_PROG_FILE := $(realpath $(CONFIG_PROG))
export CONFIG_PROG_FILE
endif

all: tools
	@echo "Building CONFIG loader"
	$(MAKE) -C src all

tools:
	@echo "Building tools"
	$(MAKE) -C tools all
	$(MAKE) -C src zx0unpack

clean:
	$(MAKE) -C src clean
	rm -f autorun-zx0.atr
	rm -rf dist

cleantools:
	$(MAKE) -C tools clean

cleanall: clean cleantools

dist: all
	@echo "Building ATR disk image"
	mkdir -p dist
	cp src/cloader.zx0 dist/
	cp src/config.com dist/
	cp ../fujinet-config-tools/atari/dist/*.COM dist/ || true
	cp ../fujinet-config-tools/atari/dist/*.com dist/ || true
	rm -f autorun-zx0.atr
	dir2atr $(DENSITYOPT) -B src/zx0boot.bin autorun-zx0.atr dist/
	tools/update-atr.py autorun-zx0.atr cloader.zx0 config.com

