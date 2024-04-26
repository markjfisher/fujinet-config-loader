# 
# FujiNet Config Loader Makefile - stripped down version of MyPicoDos Makefile
#
# MyPicoDos Makefile (c) 2003-2017 by Matthias Reichl <hias@horus.com>
# 2021-2024 apc.atari@gmail.com - modified for FujiNet Config Loader
#

ATASM ?= ../tools/atasm/atasm

PROGS := zx0boot.bin cloader.zx0 config.com

# default target file to compress if not set
ifndef CONFIG_PROG_FILE
	CONFIG_PROG_FILE := ../../fujinet-config/config.com
endif
# $(info CONFIG_PROG_FILE=$(CONFIG_PROG_FILE))

# Loader customization - optional parameters for make
# USEHISIO : 1 to include HISIO code (default)
#            0 to not include/use HISIO code
# USECACHE : 1 to include disk cache code (uses RAM under OS or XE extended RAM or Axlon RAM)
#            0 to not include/use disk cache code
# DENSITY  : SD to produce SD ATR disk image (default)
#            DD to produce DD ATR disk image
# RESTOREDMA: 0 - DMA is not enabled (default), only Display List is restored
#               this prevents screen "blink" when switching from Loader to CONFIG
#               it is assumed config will enable DMA, e.g when setting up PMG
#             1 - DMA is enabled and colors are set to default, Display List is restored
#               could be useful for alternate config program which does expect DMA
#               is enabled
# SIOSOUND : 0 for silent SIO (default)
#            1 to keep SIO audible
# LOADBAR  : 0 to do not show progress bar while loading
#          : 1 to show progress bar while loading (default)
LOADERFLAGS :=

USEHISIO := 1
ifneq ($(USEHISIO), 0)
	LOADERFLAGS += -DHIGHSPEED=1
endif

USECACHE := 0
ifneq ($(USECACHE), 0)
	LOADERFLAGS += -DDISKCACHE=1
endif

# DENSITY := SD
ifeq ($(DENSITY), DD)
	LOADERFLAGS += -DDOUBLEDENSITY=1
endif

RESTOREDMA := 0
ifneq ($(RESTOREDMA), 0)
	LOADERFLAGS += -DRESTOREDMA=1
endif

SIOSOUND := 0
ifneq ($(SIOSOUND), 0)
	LOADERFLAGS += -DSIOSOUND=1
endif

LOADBAR := 1
ifneq ($(LOADBAR), 0)
	LOADERFLAGS += -DLOADBAR=1
endif


# Banner customization - optional parameters for make
# BANNERMODE : "F" for Antic mode F (default)
#              "E" for Antic mode E
#              "none" to disable banner (only progress bar will be shown)
# BANNERSIZE : "small" (default) for 1024 bytes bitmap, 256x32 in mode F or 128x32 in mode E
#              "medium" for 2048 bytes bitmap, 256x64 in mode F or 128x64 in mode E
#              "large" for 4000 bytes bitmap, 256x125 in mode F or 128x125 in mode E
# BANNERNAME : Specifies what banner data and colors will be used.
#              The name of the banner data file consists of:
#              $(BANNERNAME)-mode-$(BANNERMODE)-$(BANNERSIZE).banner.dat
#              this file must exist in "data" directory
#              default BANNERNAME value is "default"
#              i.e. default banner data file is default-mode-F-small-banner.dat
#              and default colors file is default-mode-F-small-colors.dat
# BANNERLOAD : Banner bitmap loading address (decimal)
#
# Example: make BANNERNAME=vcf BANNERMODE=E BANNERSIZE=large BANNERLOAD=32768

BANNERNAME  := default
BANNER_FILE := $(BANNERNAME)
BANNERFLAGS :=

# BANNERMODE = E|F|none => -DBANNERMODE = 14|15|0 for Atasm
ifdef BANNERMODE
FLAG :=
ifeq ($(BANNERMODE), E)
	FLAG := -DBANNERMODE=14
endif
ifeq ($(BANNERMODE), F)
	FLAG := -DBANNERMODE=15
endif
ifeq ($(BANNERMODE), none)
	FLAG := -DBANNERMODE=0
	SKIPSIZEPART := 1
endif
ifdef FLAG
# $(info BANNERMODE="$(BANNERMODE)" => $(FLAG))
	BANNERFLAGS += $(FLAG)
	BANNER_FILE := $(BANNER_FILE)-mode-$(BANNERMODE)
else
$(error Inavlid BANNERMODE "$(BANNERMODE)")
endif
else
	BANNER_FILE := $(BANNER_FILE)-mode-F
endif # BANNERMODE

# BANNERSIZE = small|medium|large => -DBANNERSIZE= 1|2|3 for Atasm
ifdef BANNERSIZE
FLAG :=
ifeq ($(BANNERSIZE), small)
	FLAG := -DBANNERSIZE=1
endif
ifeq ($(BANNERSIZE), medium)
	FLAG := -DBANNERSIZE=2
endif
ifeq ($(BANNERSIZE), large)
	FLAG := -DBANNERSIZE=3
endif
ifdef FLAG
# $(info BANNERSIZE="$(BANNERSIZE)" => $(FLAG))
	BANNERFLAGS += $(FLAG)
ifndef SKIPSIZEPART
	BANNER_FILE := $(BANNER_FILE)-$(BANNERSIZE)
endif
else
$(error Inavlid BANNERSIZE "$(BANNERSIZE)")
endif
else
ifndef SKIPSIZEPART
	BANNER_FILE := $(BANNER_FILE)-small
endif
endif # BANNERSIZE

COLORS_FILE := $(BANNER_FILE)-colors.dat
BANNER_FILE := $(BANNER_FILE)-banner.dat

# BANNERLOAD => -DBANNERLOAD=..
ifdef BANNERLOAD
	BANNERFLAGS += -DBANNERLOAD=$(BANNERLOAD)
endif

# HISIO routines
ASMFLAGS := -Ihisio
HISIOINC := hisio/hisio.inc hisio/hisiocode.src hisio/hisiodet.src \
        hisio/hisiocode-break.src hisio/hisiocode-cleanup.src \
        hisio/hisiocode-main.src hisio/hisiocode-send.src \
        hisio/hisiocode-check.src hisio/hisiocode-diag.src \
        hisio/hisiocode-receive.src hisio/hisiocode-vbi.src

LOADERSOURCES := cloader-lo.src cloader-hi.src zx0boot.src dzx0.src $(HISIOINC)
LOADERDATA := ../data/banner.dat ../data/colors.dat

.PHONY: all clean zx0unpack datafiles

all: datafiles $(PROGS)

clean:
	rm -f *.obj *.bin *.lst
	rm -f $(PROGS)
	rm -f ../data/banner.dat ../data/colors.dat

datafiles:
	cmp -s ../data/$(BANNER_FILE) ../data/banner.dat || cp -v ../data/$(BANNER_FILE) ../data/banner.dat
	cmp -s ../data/$(COLORS_FILE) ../data/colors.dat || cp -v ../data/$(COLORS_FILE) ../data/colors.dat

# ZX0 capable boot loader, 3 sectors
zx0boot.bin: zx0boot.src dzx0.src
	@echo "Building boot loader"
	$(ATASM) $(ASMFLAGS) -r $(LOADERFLAGS) -gzx0boot.lst -o$@ $<

# config loader low part - contains HISIO routines and INIT to activate them
cloader-lo.obj: $(LOADERSOURCES) $(LOADERDATA)
	@echo "Building config loader - low part"
	$(ATASM) $(ASMFLAGS) $(LOADERFLAGS) $(BANNERFLAGS) -gcloader-lo.lst -o$@ cloader-lo.src

# config loader high part - config loader, display list, progress bar, banner
cloader-hi.obj: $(LOADERSOURCES) $(LOADERDATA)
	@echo "Building config loader - high part"
	$(ATASM) $(ASMFLAGS) -dPARTHI=1 $(LOADERFLAGS) $(BANNERFLAGS) -gcloader-hi.lst -o$@ cloader-hi.src

# join low and high parts into one file
cloader.obj: cloader-lo.obj cloader-hi.obj
	cat cloader-lo.obj cloader-hi.obj > $@

# ZX0 compressed version of config loader
cloader.zx0: cloader.obj
	@echo "Building config loader - ZX0 compressed"
	../tools/a8pack.py -c -f -v $< $@


# relocatable ZX0 decompressor
zx0unpack: ../tools/pack/a8/zx0unpack.obj

../tools/pack/a8/zx0unpack.obj: zx0unpack-1000.obj zx0unpack-1201.obj
	@echo "Building relocatable ZX0 decompressor"
	../tools/relgen.py zx0unpack-1000-f.obj zx0unpack-1201-f.obj $@

# decompressor build to $1000
zx0unpack-1000.obj: zx0unpack.src dzx0.src
	$(ATASM) $(ASMFLAGS) -dUNPACKER=1 -dUNPACKSTART=4096 -gzx0unpack.lst -o$@ $<
	../tools/a8pack.py -f $@ zx0unpack-1000-f.obj

# decompressor build to $1201
zx0unpack-1201.obj: zx0unpack.src dzx0.src
	$(ATASM) $(ASMFLAGS) -dUNPACKER=1 -dUNPACKSTART=4609 -o$@ $<
	../tools/a8pack.py -f $@ zx0unpack-1201-f.obj

# compressed CONFIG, DOS compatible self-extracting, Loader compatible w/ inline decompression
config.com: $(CONFIG_PROG_FILE)
	@echo "Building compressed CONFIG"
	../tools/a8pack.py -d -v $< $@

