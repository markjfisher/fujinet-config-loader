#!/usr/bin/env python3

import sys, os
import math
from PIL import Image


def palette_to_colors(palette):
    return [
        (palette[n],palette[n+1],palette[n+2]) for n in range(0, len(palette), 3)
    ]

def colors_to_palette(rgb_list):
    palette = []
    for rgb in rgb_list:
        palette.extend(rgb)
    return palette

def color_distance(rgb1, rgb2):
    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    r = r1 - r2
    g = g1 - g2
    b = b1 - b2
    r_mean = (r1 + r2) / 2

    return math.sqrt(
        (512 + r_mean) / 256 * r ** 2 # >> 8 is same as dividing by 256
      + 4 * g ** 2
      + (767 - r_mean) / 256 * b ** 2)

max_color_distance = color_distance((0,0,0), (255,255,255))


def color_distance_norm(rgb1, rgb2):
    return color_distance(rgb1, rgb2) / max_color_distance


def match_palette_color(rgb, rgb_palette):
    d_min = 2.0
    n_min = 0
    for n, p_rgb in enumerate(rgb_palette):
        d = color_distance_norm(rgb, p_rgb)
        if d < d_min:
            n_min, d_min = n, d
    print("best match: {} -> {} @ {} 0x{:02x} d={}".format(rgb, rgb_palette[n_min], n_min, n_min, d_min))
    return n_min, rgb_palette[n_min]


def remap_palette_colors(rgb_pal1, rgb_pal2):
    new_rgb_pal = []
    for rgb in rgb_pal1:
        _, new_rgb = match_palette_color(rgb, rgb_pal2)
        new_rgb_pal.append(new_rgb)
    return new_rgb_pal

def pixels_to_bytes(img:Image):
    def pack_bytes():
        n, b = 0, 0
        for value in img.getdata():
            b = (b<<2) | (value&3)
            n += 1
            if n == 4:
                yield b
                n, b = 0, 0
    return bytes(pack_bytes())

def colors_to_bytes(rgb_pal1, rgb_pal2):
    a8color = [match_palette_color(rgb, rgb_pal2)[0] for rgb in rgb_pal1]
    return bytes((
        a8color[1],
        a8color[2],
        a8color[3],
        a8color[0],
        a8color[0]
    ))

for img_fname in sys.argv[1:]:
    #palette = [ 0,0,0, 0x9b,0xc8,0xc7, 0x4b,0xaf,0xb4, 0x33,0x5d,0x5e]

    dirname = os.path.dirname(os.path.realpath(sys.argv[0]))

    with open(os.path.join(dirname, "PAL.pal"), "rb") as f:
        pal_palette = f.read()
        pal_colors = palette_to_colors(pal_palette)
    with open(os.path.join(dirname, "NTSC.pal"), "rb") as f:
        ntsc_palette = f.read()
        ntsc_colors = palette_to_colors(ntsc_palette)
    #match_palette_color((0x9b,0xc8,0xc7), pal_colors)

    orig_img = Image.open(img_fname)
    orig_img = orig_img.convert("RGB")
    # resize
    new_img = orig_img
    #new_img = orig_img.resize((int(orig_img.width * 125 / orig_img.height) ,125), Image.LANCZOS)
    #new_img = orig_img.resize((int(orig_img.width * 32 / orig_img.height) ,32), Image.LANCZOS)

    # note: this produced bad results
    # # apply atari palette
    # pal_img = Image.new("P", (16, 16), 0)
    # pal_img.putpalette(ntsc_palette)
    # new_img = new_img.quantize(palette=pal_img, dither=Image.Dither.NONE)
    # new_img = new_img.convert("RGB")

    # convert to palette image and reduce colors
    # note: reduction does produce unusable result when reducing directly to 4 colors
    pal_img = new_img.quantize(colors=6, dither=Image.Dither.NONE)
    # get first 4 colors (out of 6) from palette
    colors = palette_to_colors(pal_img.getpalette()[:12])
    # make blank image, set our palette
    pal_img = Image.new("P", (16, 16), 0)

    # adjust order of colors in palette:
    # color[0] used for border (and background in mode E)
    # color[1] "empty" part of progress bar, color[2] "processed" part of progress bar
    # a) reverse order of all color
    colors.reverse()
    # b) swap colors for progress bar
    # c1, c2 = colors[1], colors[2]
    # colors[1], colors[2] = c2, c1

    pal_img.putpalette(colors_to_palette(colors))
    # now reduce colors again, this time with help of our 4-color palette image
    new_img = new_img.quantize(palette=pal_img, dither=Image.Dither.FLOYDSTEINBERG)

    # replace palette colors with colors from atari palette
    palette = new_img.getpalette()
    # NTSC palette
    img_colors_ntsc = remap_palette_colors(palette_to_colors(palette), ntsc_colors)
    # PAL palette
    img_colors_pal = remap_palette_colors(palette_to_colors(palette), pal_colors)

    # save picture
    dirname, filename = os.path.split(img_fname)
    name, ext = os.path.splitext(filename)
    # NTSC version
    img_fname_new = os.path.join(dirname, "%s-ntsc.png" % name)
    new_img.putpalette(colors_to_palette(img_colors_ntsc))
    new_img.save(img_fname_new)
    # PAL version
    img_fname_new = os.path.join(dirname, "%s-pal.png" % name)
    new_img.putpalette(colors_to_palette(img_colors_pal))
    new_img.save(img_fname_new)

    # save Atari picture (video ram content)
    with open("banner.dat", "wb") as f:
        f.write(pixels_to_bytes(new_img))

    # save Atari palette (color registers, NTSC and PAL version)
    with open("colors.dat", "wb") as f:
        f.write(colors_to_bytes(img_colors_ntsc, ntsc_colors))
        f.write(colors_to_bytes(img_colors_pal, pal_colors))
