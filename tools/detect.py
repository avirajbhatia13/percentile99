#!/usr/bin/env python3
"""
Green-tick answer detector for SOLVED CAT papers (digialm / FundaMakers format).

Scans the narrow left band of a rendered question page where the ✓ / ✗ glyph sits,
classifies each row as Green (correct) or Red (wrong), and returns the marks
top-to-bottom. For a clean single-question page you get exactly 4 marks with one
green — the green's 0-based position is the answer index.

Usage:
    python3 tools/detect.py page_042.png            # -> ['R','R','R','G']
    python3 tools/detect.py page_*.png              # batch

RELIABILITY: trust ONLY when a page returns exactly 4 marks and exactly 1 green.
If you get >4 marks or multiple greens (long green-coloured option text, or two
questions on one page), open the page image and read the ✓ by eye instead.
"""
import sys
from PIL import Image


def marks(fn):
    im = Image.open(fn).convert('RGB')
    W, H = im.size
    px = im.load()
    x0, x1 = int(0.07 * W), int(0.18 * W)   # left tick-band only
    rows = []
    for y in range(H):
        g = r = 0
        for x in range(x0, x1):
            R, G, B = px[x, y][:3]
            if G > 170 and G - R > 55 and G - B > 55:      # green ✓
                g += 1
            elif R > 195 and R - G > 105 and R - B > 105:  # red ✗
                r += 1
        rows.append((g, r))
    # collapse consecutive coloured rows into marks (blank gap > 7 rows separates)
    mk = []
    cur = None
    blank = 0
    for y, (g, r) in enumerate(rows):
        c = 'G' if g >= 3 else ('R' if r >= 3 else None)
        if c:
            if cur is None:
                cur = {'ys': [], 'g': 0, 'r': 0}
            cur['ys'].append(y)
            cur['g'] += (c == 'G')
            cur['r'] += (c == 'R')
            blank = 0
        else:
            if cur is not None:
                blank += 1
                if blank > 7:
                    mk.append(cur)
                    cur = None
                    blank = 0
    if cur:
        mk.append(cur)
    out = []
    for m in mk:
        if m['ys'][-1] - m['ys'][0] + 1 < 10:   # ignore specks
            continue
        out.append((sum(m['ys']) / len(m['ys']), 'G' if m['g'] >= m['r'] else 'R'))
    out.sort()
    return [c for _, c in out]


def answer_index(cols):
    """For a clean single-question page: return the green index, else a diagnostic."""
    if len(cols) == 4 and cols.count('G') == 1:
        return cols.index('G')
    if 'G' in cols:
        return 'AMBIGUOUS rbg=%d marks=%d greens=%d (VISION-CHECK)' % (
            cols.index('G'), len(cols), cols.count('G'))
    return 'NO-GREEN marks=%d (VISION-CHECK)' % len(cols)


if __name__ == '__main__':
    for fn in sys.argv[1:]:
        c = marks(fn)
        print(fn, c, '->', answer_index(c))
