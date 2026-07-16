#!/usr/bin/env python3
"""
Crop a figure (chart / diagram / table image) out of a rendered PDF page and
auto-trim surrounding whitespace. Saves under img/pyq/<year>/<slot>/<name>.png.

Usage:
    python3 tools/crop_figure.py page_069.png img/pyq/2023/s1/orders-gantt.png \
        --box 0.10 0.06 0.68 0.285

--box is left top right bottom as FRACTIONS of page width/height. Start generous,
then look at the output and tighten. The script auto-trims whitespace inside the box
and pads 8px, so a slightly-too-large box is fine as long as it isn't clipping the figure.
"""
import argparse
import os
from PIL import Image, ImageChops


def crop(src, dst, box, pad=8):
    im = Image.open(src).convert('RGB')
    W, H = im.size
    l, t, r, b = box
    c = im.crop((int(l * W), int(t * H), int(r * W), int(b * H)))
    bbox = ImageChops.difference(c, Image.new('RGB', c.size, (255, 255, 255))).getbbox()
    if bbox:
        bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
                min(c.width, bbox[2] + pad), min(c.height, bbox[3] + pad))
        c = c.crop(bbox)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    c.save(dst)
    print('saved', dst, c.size)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src')
    ap.add_argument('dst')
    ap.add_argument('--box', nargs=4, type=float, default=[0.10, 0.06, 0.68, 0.30],
                    metavar=('L', 'T', 'R', 'B'))
    ap.add_argument('--pad', type=int, default=8)
    a = ap.parse_args()
    crop(a.src, a.dst, a.box, a.pad)
