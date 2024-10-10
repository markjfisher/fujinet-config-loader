# FujiNet Config Loader


This is loader for [Atari FujiNet Config](https://github.com/FujiNetWIFI/fujinet-config) program. It uses high speed SIO routines and ZX0 decompression for faster config load. When loading, the banner is shown and simple progress bar is being updated.

<img src="loader.png" alt="loader" width="400"/>

The code relies on high speed SIO routines. HISIO is part of [MyPicoDos](https://www.horus.com/~hias/atari/#mypdos), a "gamedos" for the 8-bit Ataris, written by HiassofT.

Another key component used to accelerate the loading is the [ZX0](https://github.com/einar-saukas/ZX0)  compression by Einar Saukas. Decompression routine was ported to [6502](https://xxl.atari.pl/zx0-decompressor/) by Krzysztof 'XXL' Dudek.

## How it works

Without config loader, PicoBoot boot loader loads directly FujiNet's CONFIG program.

Config loader uses ZX0 capable boot loader instead of PicoBoot. ZX0 boot loader can load regular Atari COM files as well files with ZX0 compressed segments. It allows decompression of data while loading.

The config loader is loaded and started by boot loader. Then ZX0 compressed CONFIG is loaded using HISIO and ZX0 decompression routines. Read sector routines are hooked up to allow progress bar updates.

## How to compile

HISIO code comes from MyPicoDos, so ATASM is needed to compile it (ATASM was added into `tools` directory).

Prepare and build FujiNet CONFIG program as usually, inside directory `fujinet-config`, as well ensure recent FujiNet Config Tools are available in `fujinet-config-tools` directory. Directory `fujinet-config-loader` must be at the same level as previous two.

```sh
make clean && make dist
```

Note: To rebuild `tools` directory use `make cleanall` instaed of `make clean`.

If everything goes fine, there will be new ATR image called `autorun-zx0.atr`. ATR content:
```
CLOADER.ZX0     - ZX0 compressed config loader with bundled HISIO routines and banner bitmap
CONFIG.COM      - ZX0 compressed CONFIG programm in format compatible with Atari DOS
...             - all FujiNet Config Tools like FLD, FLH, NCD, NCOPY, FMALL, etc.
```

## Customization

To customize the config loader there are some variables which can be used with make command:

```
DENSITY         - Disk density, can be SD (default) or DD

CONFIG_PROG     - Path to alternate CONFIG program

USEHISIO        - Controls if high speed SIO code will be part of config loader
                  1 (default) to include high speed SIO code
                  0 do not include high speed SIO

USECACHE        - Controls if disk sector caching code will be part of config loader
                  Disk cache uses RAM under OS or XE extended RAM or Axlon RAM.
                  1 to include disk cache code 
                  0 do not include disk cache code

RESTOREDMA      - If DMA should be enabled when Loader is done before starting Config
                  0 (default) DMA is not enabled, only Display List is restored
                  this prevents screen "blink" when switching from Loader to Config
                  it is assumed Config will enable DMA, e.g when setting up P-M Graphics
                  1 DMA is enabled and colors are set to defaults, Display List is restored
                  This could be useful for alternate config program which does expect the DMA
                  is enabled.

SIOSOUND        - Audible SIO reads
                  0 for silent SIO (default)
                  1 to keep SIO audible

LOADBAR         - Loading progress bar
                  0 to do not use progress bar to indicate loading progress
                  1 (default) to show progress bar while loading
```

Additional variables can be used to customize the banner bitmap:

```
BANNERMODE      - Antic mode for banner bitmap
                  E (4 colors), F (mono, default) or none (to disable banner)

BANNERSIZE      - Size of banner bitmap 
                  small (default) for 1024 bytes bitmap, 256x32 in mode F or 128x32 in mode E
                  medium for 2048 bytes bitmap, 256x64 in mode F or 128x64 in mode E
                  large for 4000 bytes bitmap, 256x125 in mode F or 128x125 in mode E

BANNERNAME      - Specifies what banner data and colors will be added into Loader.
                  The name of the banner data file consists of:
                  $(BANNERNAME)-mode-$(BANNERMODE)-$(BANNERSIZE).banner.dat
                  this file must exist in "data" directory
                  default BANNERNAME is "default"
                  i.e. default banner data file is default-mode-F-small-banner.dat
                  and default colors file is default-mode-F-small-colors.dat

BANNERLOAD      - Banner bitmap loading address (decimal)
```

Example:
```sh
make BANNERNAME=vcf BANNERMODE=E BANNERSIZE=large BANNERLOAD=32768 clean dist
```

## Generating images to use

1. Create an image in gimp with aspect ratio as per target banner size (e.g. 128x125 for mode E)
2. Convert to 4 colours
3. Scale down to dimensions as given in BANNERSIZE above, e.g. mode F 128x125
4. Save the image as png file

5. Now run the convert script:

```sh
tools/convert-picture.py /path/to/your-image.png
```
   The output will be in root dir as `banner.dat` and `colors.dat`.

6. Move these files to the `data/` directory with a new name, e.g. `my-logo-mode-E-large-banner.dat` and similar for colours file.
7. You can now build your application with the appropriate banner configuration, e.g

```sh
make BANNERNAME=my-logo BANNERMODE=E BANNERSIZE=large BANNERLOAD=32768 clean dist
```
