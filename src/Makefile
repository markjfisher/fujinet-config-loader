# 
# FujiNet Config Loader Makefile - stripped down version of MyPicoDos Makefile
#
# MyPicoDos Makefile (c) 2003-2017 by Matthias Reichl <hias@horus.com>
# 2021 apc.atari@gmail.com - modified for FujiNet Config Loader
#

ATASM ?= ../tools/atasm/atasm

PROGS := zx0boot.bin cloader.zx0 config.com

# default target file to compress if not set
ifndef CONFIG_COM_FILE
	CONFIG_COM_FILE := ../../fujinet-config/config.com
endif
$(info CONFIG_COM_FILE=$(CONFIG_COM_FILE))

# Loader customization - optional parameters for make
# USEHISIO : 1 to include HISIO code (default)
#            0 to not include/use HISIO code
# USECACHE : 1 to include disk cache code (uses RAM under OS or XE extended RAM or Axlon RAM)
#            0 to not include/use disk cache code
# DENSITY :  SD to produce SD ATR disk image (default)
#            DD to produce DD ATR disk image
LOADERFLAGS :=

USEHISIO := 1
ifneq ($(USEHISIO), 0)
	LOADERFLAGS += -DHIGHSPEED=1
endif

USECACHE := 1
ifneq ($(USECACHE), 0)
	LOADERFLAGS += -DDISKCACHE=1
endif

# DENSITY := SD
ifeq ($(DENSITY), DD)
	LOADERFLAGS += -DDOUBLEDENSITY=1
endif

# Banner customization - optional parameters for make
# BANNERMODE : E for Antic mode E (defult)
#              F for Antic mode F
#              NONE to disable banner (only progress bar will be shown)
# BANNERSIZE : SMALL (default) for 1024 bytes bitmap, 256x32 in mode F or 128x32 in mode E
#              MEDIUM for 2048 bytes bitmap, 256x64 in mode F or 128x64 in mode E
#              LARGE for 4000 bytes bitmap, 256x125 in mode F or 128x125 in mode E
# BANNERLOAD : banner load address (decimal)
#
# Example: make BANNERMODE=E BANNERSIZE=LARGE BANNERLOAD=32768
BANNERFLAGS :=

 # BANNERMODE => -DBANNERMODE=..
ifdef BANNERMODE
FLAG :=
ifeq ($(BANNERMODE), E)
	FLAG := -DBANNERMODE=14
endif
ifeq ($(BANNERMODE), F)
	FLAG := -DBANNERMODE=15
endif
ifeq ($(BANNERMODE), NONE)
	FLAG := -DBANNERMODE=0
endif
ifdef FLAG
$(info BANNERMODE="$(BANNERMODE)" => $(FLAG))
	BANNERFLAGS += $(FLAG)
else
$(error Inavlid BANNERMODE "$(BANNERMODE)")
endif
endif # BANNERMODE

# BANNERSIZE => -DBANNERSIZE=..
ifdef BANNERSIZE
FLAG :=
ifeq ($(BANNERSIZE), SMALL)
	FLAG := -DBANNERSIZE=1
endif
ifeq ($(BANNERSIZE), MEDIUM)
	FLAG := -DBANNERSIZE=2
endif
ifeq ($(BANNERSIZE), LARGE)
	FLAG := -DBANNERSIZE=3
endif
ifdef FLAG
$(info BANNERSIZE="$(BANNERSIZE)" => $(FLAG))
	BANNERFLAGS += $(FLAG)
else
$(error Inavlid BANNERSIZE "$(BANNERSIZE)")
endif
endif # BANNERSIZE

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

.PHONY: all clean zx0unpack

all: $(PROGS)

clean:
	rm -f *.obj *.bin *.lst
	rm -f $(PROGS)


# ZX0 capable boot loader, 3 sectors
zx0boot.bin: zx0boot.src dzx0.src
	@echo "Building boot loader"
	$(ATASM) $(ASMFLAGS) -r $(LOADERFLAGS) -gzx0boot.lst -o$@ $<

# config loader low part - contains HISIO routines and INIT to activate them
cloader-lo.obj: $(LOADERSOURCES)
	@echo "Building config loader - low part"
	$(ATASM) $(ASMFLAGS) $(LOADERFLAGS) $(BANNERFLAGS) -gcloader-lo.lst -o$@ cloader-lo.src

# config loader high part - config loader, display list, progress bar, banner
cloader-hi.obj: $(LOADERSOURCES)
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
	../tools/relgen.py zx0unpack-1000-f.obj zx0unpack-1201-f.obj ../tools/pack/a8/zx0unpack.obj

# decompressor build to $1000
zx0unpack-1000.obj: zx0unpack.src dzx0.src
	$(ATASM) $(ASMFLAGS) -dUNPACKER=1 -dUNPACKSTART=4096 -gzx0unpack.lst -o$@ $<
	../tools/a8pack.py -f zx0unpack-1000.obj zx0unpack-1000-f.obj

# decompressor build to $1201
zx0unpack-1201.obj: zx0unpack.src dzx0.src
	$(ATASM) $(ASMFLAGS) -dUNPACKER=1 -dUNPACKSTART=4609 -o$@ $<
	../tools/a8pack.py -f zx0unpack-1201.obj zx0unpack-1201-f.obj

# compressed CONFIG, DOS compatible self-extracting, Loader compatible w/ inline decompression
config.com: $(CONFIG_COM_FILE)
	@echo "Building compressed CONFIG"
	../tools/a8pack.py -d -v $< config.com

