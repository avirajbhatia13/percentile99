#!/usr/bin/env python3
"""
Poppler-free PDF render/extract helper (uses PyMuPDF). Drop-in stand-in for
pdftoppm/pdftotext/pdfinfo on machines where poppler-utils isn't installed
(e.g. this Windows dev box) — same page-numbering convention, so the rest of
docs/INGEST_FRAMEWORK.md reads unchanged.

    pip install pymupdf

Usage:
    python tools/render_pdf.py paper.pdf --info
        -> prints page count                              (stand-in: pdfinfo)

    python tools/render_pdf.py paper.pdf pages_ --dpi 150 --first 1 --last 20
        -> writes pages_001.png .. pages_020.png           (stand-in: pdftoppm)

    python tools/render_pdf.py paper.pdf --first 1 --last 20 --text paper.txt
        -> writes paper.txt, pages joined with form-feed   (stand-in: pdftotext -layout)

--first/--last are 1-based and inclusive, matching pdftoppm -f/-l.
"""
import argparse
import pymupdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('prefix', nargs='?', help='output PNG prefix, e.g. pages_')
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--first', type=int, default=1)
    ap.add_argument('--last', type=int, default=None)
    ap.add_argument('--text', help='also write extracted text to this path')
    ap.add_argument('--info', action='store_true', help='print page count and exit')
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    if a.info:
        print('Pages:', doc.page_count)
        return

    last = a.last or doc.page_count
    width = max(3, len(str(last)))
    mat = pymupdf.Matrix(a.dpi / 72.0, a.dpi / 72.0)
    texts = []
    for n in range(a.first, last + 1):
        page = doc[n - 1]
        if a.prefix:
            fn = f'{a.prefix}{n:0{width}d}.png'
            page.get_pixmap(matrix=mat).save(fn)
            print('wrote', fn)
        if a.text:
            texts.append(page.get_text('text'))
    if a.text:
        with open(a.text, 'w', encoding='utf-8') as f:
            f.write('\x0c'.join(texts))
        print('wrote', a.text)


if __name__ == '__main__':
    main()
