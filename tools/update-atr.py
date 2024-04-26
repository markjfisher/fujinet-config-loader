#!/usr/bin/env python3

#
# update-atr.py - to update CLOADER file with size and start sector of CONFIG
#
#  2021-2024 apc.atari@gmail.com
#


import sys
import struct


def atari_filename(fname):
    s = fname.split('.')
    name = s[0][0:8]
    if len(name) < 8:
        name += ' ' * (8-len(name))
    if len(s) > 1:
        ext = s[1][0:3]
        if len(ext) < 3:
            ext += ' ' * (3-len(ext))
    else:
        ext = '   '
    return (name+ext).upper().encode("ASCII")


def _sector_offset(sector, bps):
    if sector == 1:
        offset = 16
    elif sector == 2:
        if bps == 512:
            offset = 528
        else:
            offset = 144
    elif sector == 3:
        if bps == 512:
            offset = 1040
        else:
            offset = 272
    else:
        if bps == 512:
            offset = sector * 512 + 16
        elif bps == 256:
            offset = ((sector - 3) * 256) + 16 + 128
        else:
            offset = ((sector - 1) * 128) + 16
    return offset


def get_dentry(atr, fname, bps=128):
    a8fname = atari_filename(fname)
    for sec in range(361, 369):
        for di in range(8):
            dentry_offset = _sector_offset(sec, bps) + 16*di
            dentry = atr[dentry_offset:dentry_offset+16]
            flag = dentry[0]
            if flag == 0:
                return None
            if flag & 0x80:
                continue
            # count, ssn = struct.unpack('<HH', dentry[1:5])
            dentry_fname = dentry[5:]
            # print(f"{flag:02X} {count:04X} {ssn:04X}", dentry_fname)
            if a8fname == dentry_fname:
                dentry = atr[dentry_offset:dentry_offset+16]
                return dentry
    return None


def main():
    if len(sys.argv) != 4:
        print("Usage: update-atr.py atr_file loader_name payload_name")
        sys.exit(1)

    atrfn = sys.argv[1]
    loader_name = sys.argv[2]
    payload_name = sys.argv[3]

    try:
        with open(atrfn, 'rb') as atrf:
            atr = bytearray(atrf.read())
    except Exception as e:
        print(f'Failed to read "{atrfn}"')
        print(e)
        sys.exit(-1)

    magic = struct.unpack('<H', atr[0:2])[0]
    if magic != 0x0296:
        print("ATR header missing 'NICKATARI'")
        sys.exit(-1)
    bps = struct.unpack('<H', atr[4:6])[0]

    loader_dentry = get_dentry(atr, loader_name, bps)
    if loader_dentry is None:
        print(f'Cannot find "{loader_name}" in "{atrfn}"')
        sys.exit(-1)
    
    payload_dentry = get_dentry(atr, payload_name, bps)
    if payload_dentry is None:
        print(f'Cannot find "{payload_name}" in "{atrfn}"')
        sys.exit(-1)
    
    sector_count, start_sector = struct.unpack('<HH', loader_dentry[1:5])
    print(f'Found "{loader_dentry[5:].decode("utf-8")}" {sector_count} sectors, starting at sector {start_sector}')
    if start_sector != 4:
        print("To get the file booted by ZX0 boot loader the start sector should be 4!")

    sector_count, loaded_ssn = struct.unpack('<HH', payload_dentry[1:5])
    print(f'Found "{payload_dentry[5:].decode("utf-8")}" {sector_count} sectors, starting at sector {loaded_ssn}')

    pbsf = 49 * 256 // (max(sector_count, 3) - 2)
    if pbsf > 65535: # should not happen
        print("Progress bar speed factor overflow.")
        pbsf = 65535

    # offset to config loader file + skip 6 bytes header (FFFF,START,END,...)
    offset = _sector_offset(start_sector, bps) + 6
    print("Updating ATR ... {:06X} : {:02X} {:02X} {:02X} {:02X}".format(
        offset, loaded_ssn & 0xFF, loaded_ssn >> 8, pbsf & 0xFF, pbsf >> 8))
    # update 4 bytes
    atr[offset:offset+4] = loaded_ssn & 0xFF, loaded_ssn >> 8, pbsf & 0xFF, pbsf >> 8
    # save
    try:
        with open(atrfn, 'wb') as atrf:
            atrf.write(atr)
    except Exception as e:
        print(f'Failed to write "{atrfn}"')
        print(e)
        sys.exit(-1)

    print("Done.")


if __name__ == '__main__':
    main()
