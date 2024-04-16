.PHONY: all clean


all:
	$(MAKE) -C pack/src/ZX0 all
	cp -p pack/src/ZX0/zx0 pack/
	$(MAKE) -C atasm/src all
	cp -p atasm/src/atasm atasm/

clean:
	$(MAKE) -C pack/src/ZX0 clean
	$(MAKE) -C atasm/src clean
	rm -f pack/zx0
	rm -f pack/a8/zx0unpack.obj
	rm -f atasm/atasm
