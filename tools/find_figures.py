#!/usr/bin/env python3
"""
Locate figures on a PDF page and optionally crop them, without hand-tuning box
fractions. Charts in these papers are vector drawings (plus the odd raster image),
so their extent can be read straight out of the PDF instead of eyeballed.

It clusters drawing/image rectangles by vertical position, drops the small stuff
(TITA answer boxes, rules, page furniture) and reports each cluster's bounding box
as page fractions ready for tools/crop_figure.py — or crops it directly with --save.

Usage:
    python tools/find_figures.py paper.pdf --pages 11,12          # report
    python tools/find_figures.py paper.pdf --pages 11 --save img/pyq/2024/s1/x.png
"""
import argparse
import pymupdf


def clusters(page, min_w=60, min_h=40, gap=26):
    """Bounding boxes of figure-like content, top to bottom."""
    W, H = page.rect.width, page.rect.height
    boxes = []
    for d in page.get_drawings():
        r = d['rect']
        if r.width > 3 and r.height > 3 and r.width < W * 0.97 and r.height < H * 0.9:
            boxes.append([r.x0, r.y0, r.x1, r.y1])
    for b in page.get_text('dict')['blocks']:
        if b.get('type') == 1:
            x0, y0, x1, y1 = b['bbox']
            if (x1 - x0) > 40 and (y1 - y0) > 30:
                boxes.append([x0, y0, x1, y1])
    if not boxes:
        return []
    boxes.sort(key=lambda b: b[1])
    merged = [boxes[0][:]]
    for b in boxes[1:]:
        m = merged[-1]
        if b[1] <= m[3] + gap:                      # vertically adjacent -> same figure
            m[0], m[1] = min(m[0], b[0]), min(m[1], b[1])
            m[2], m[3] = max(m[2], b[2]), max(m[3], b[3])
        else:
            merged.append(b[:])
    # drop the running header/logo band at the very top of every page
    merged = [m for m in merged if m[3] > H * 0.13]
    return [m for m in merged if (m[2] - m[0]) >= min_w and (m[3] - m[1]) >= min_h]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--pages', required=True, help='comma list, 1-based')
    ap.add_argument('--save', help='crop the FIRST cluster found to this path')
    ap.add_argument('--which', type=int, default=0, help='cluster index for --save')
    ap.add_argument('--dpi', type=int, default=200)
    ap.add_argument('--pad', type=float, default=6.0, help='padding in points')
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    for spec in a.pages.split(','):
        pno = int(spec) - 1
        page = doc[pno]
        W, H = page.rect.width, page.rect.height
        cl = clusters(page)
        print(f'page {pno + 1}: {len(cl)} figure cluster(s)')
        for i, (x0, y0, x1, y1) in enumerate(cl):
            print('  [%d] pts=(%.0f,%.0f)-(%.0f,%.0f)  --box %.4f %.4f %.4f %.4f'
                  % (i, x0, y0, x1, y1, x0 / W, y0 / H, x1 / W, y1 / H))
        if a.save and cl:
            x0, y0, x1, y1 = cl[a.which]
            clip = pymupdf.Rect(max(0, x0 - a.pad), max(0, y0 - a.pad),
                                min(W, x1 + a.pad), min(H, y1 + a.pad))
            z = a.dpi / 72
            pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip)
            pix.save(a.save)
            print('  saved', a.save, pix.width, 'x', pix.height)


if __name__ == '__main__':
    main()
