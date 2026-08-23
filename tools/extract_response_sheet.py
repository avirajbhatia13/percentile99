#!/usr/bin/env python3
"""
Draft extractor for "testbook.com candidate response sheet" PDFs (the CAT 2023
format used here — a bordered box per MCQ/SA question, page repeats the full
passage/context each time, and several short QA/VARC questions can share one
page). Produces a per-question DRAFT for manual review — it is NOT a final
mocks.json writer. Always spot-check + vision-verify figures, tables and any
question this script flags ambiguous, per docs/INGEST_FRAMEWORK.md's golden rule.

Why a new tool instead of tools/detect.py: that one scans a narrow left tick-band
for a green/red glyph (digialm/FundaMakers format, CAT 2021/2022). This vendor's
PDFs mark the correct MCQ option with a colored text background instead, and (bonus)
print SA/TITA answers as plain text ("Possible Answer: X") — no vision needed there
at all. Answers are located via each question's own text bbox (from the PDF's text
layer, chunked by "Q.N" boundary), not page-level regexes — so pages with several
short questions (QA, standalone VARC) are handled correctly, not just one-question-
per-page sections (RC, DILR).

Usage:
    python tools/extract_response_sheet.py paper.pdf --first 3 --last 51 --out draft.json

Each draft record: {page, qno, section, qtype, text, opts: {1..4: {text, color}},
green, possible_answer, ambiguous}. `ambiguous` is true unless exactly one MCQ
option is green (or it's a pure SA question with a Possible Answer) — those MUST
be vision-checked by hand.
"""
import argparse
import json
import re
import pymupdf
from PIL import Image


def option_color(im, zoom, x_pt, y_pt):
    xpx, ypx = int(x_pt * zoom), int(y_pt * zoom)
    box = im.crop((xpx - 8, ypx - 6, xpx + 8, ypx + 6))
    data = list(box.getdata())
    n = len(data)
    r = sum(p[0] for p in data) / n
    g = sum(p[1] for p in data) / n
    b = sum(p[2] for p in data) / n
    if g - r > 10 and g - b > 10:
        return 'G'
    if r - g > 10 and r - b > 10:
        return 'R'
    return '?'


def process_page(doc, pno, dpi=150):
    page = doc[pno]
    d = page.get_text('dict')
    zoom = dpi / 72
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
    im = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)

    lines = []
    for b in d['blocks']:
        if b.get('type') != 0:
            continue
        for l in b['lines']:
            txt = ''.join(s['text'] for s in l['spans'])
            lines.append({'bbox': l['bbox'], 'text': txt})
    lines.sort(key=lambda ln: ln['bbox'][1])

    section = None
    for ln in lines:
        m = re.match(r'Section\s*:\s*(\w+)', ln['text'])
        if m:
            section = m.group(1)

    # split into per-question chunks at "Q.N" boundaries (left-margin column only,
    # x0 < 60, to avoid matching "Q.1" if it ever appears inside body text)
    bounds = [i for i, ln in enumerate(lines)
              if re.match(r'^Q\.(\d+)\b', ln['text'].strip()) and ln['bbox'][0] < 60]
    if not bounds:
        return [{'page': pno + 1, 'qno': None, 'section': section, 'qtype': None,
                  'preamble': '', 'text': page.get_text('text'), 'opts': {}, 'green': [],
                  'possible_answer': None, 'ambiguous': True}]

    # text before the FIRST Q.N boundary = shared passage/DILR-set context, if any
    # (dropped entirely if we only slice from the boundary onward)
    preamble = '\n'.join(c['text'] for c in lines[:bounds[0]]).strip()

    # some pages split a 2-digit "Q.11" into a "Q.1" span plus a lone "1" span that
    # drifts a line or two down (still left-margin, before "Ans"/the first option) —
    # detect and stitch the digit back on, else everything after Q.10 silently
    # misnumbers as Q.1, Q.1, Q.1 ...
    qno_of = {}
    skip_as_digit_tail = set()
    for bi, li in enumerate(bounds):
        qno = int(re.match(r'^Q\.(\d+)', lines[li]['text'].strip()).group(1))
        scan_end = bounds[bi + 1] if bi + 1 < len(bounds) else len(lines)
        for j in range(li + 1, min(scan_end, li + 6)):
            t = lines[j]['text'].strip()
            if t in ('Ans',) or re.match(r'^[1-4]\.', t):
                break
            m = re.match(r'^(\d{1,2})$', t)
            if m and abs(lines[j]['bbox'][0] - lines[li]['bbox'][0]) < 20:
                qno = int(str(qno) + m.group(1))
                skip_as_digit_tail.add(j)
                break
        qno_of[li] = qno

    records = []
    for bi, li in enumerate(bounds):
        qno = qno_of[li]
        end = bounds[bi + 1] if bi + 1 < len(bounds) else len(lines)
        chunk = [ln for i, ln in enumerate(lines[li:end], start=li) if i not in skip_as_digit_tail]
        text = '\n'.join(c['text'] for c in chunk)

        qtype = re.search(r'Question Type\s*:\s*(\w+)', text)
        # option START lines: "N. ..." at the option-number x-column. The wording
        # sometimes continues on following lines instead of the start line itself
        # (same x-column, x0<370 to stay left of the right-side metadata box) —
        # collect those into the option's text too, up to the next option/metadata.
        META_KEYS = ('Question Type', 'Question ID', 'Option', 'Status',
                     'Chosen Option', 'Case Sensitivity', 'Answer Type',
                     'Possible Answer', 'Given', 'Answer :', 'Page ')
        # option x0 drifts a few points between PDFs from this vendor (seen: ~80 in
        # one export, ~88 in another) — widen the band and sample the tick icon
        # relative to each option's OWN x0 rather than an absolute page x-coordinate.
        # SA/TITA questions never have real MCQ options — a stray "N. ..."-shaped
        # line inside a numbered-sentence stem (para-jumble etc.) can otherwise be
        # mistaken for one, which then wrongly disables the possible_answer path.
        is_sa = qtype and qtype.group(1) == 'SA'
        # Real options always sit BETWEEN the stem and the question's metadata block. Some
        # exports repeat the whole passage/DILR-set context inside every question box, so
        # the *next* question's context (and its "1. ... 2. ..." clue list) can trail inside
        # this chunk — scanning the whole chunk lets those clues overwrite the real options.
        body = chunk[:next((i for i, ln in enumerate(chunk)
                            if ln['text'].startswith(('Question Type', 'Case Sensitivity'))),
                           len(chunk))]
        starts = [] if is_sa else [(i, int(m.group(1)), m.group(2))
                  for i, ln in enumerate(body)
                  if (m := re.match(r'^\s*([1-4])\.\s?(.*)', ln['text']))
                  and 70 <= ln['bbox'][0] <= 100]
        opts = {}
        for si, (i, n, first_text) in enumerate(starts):
            y = (chunk[i]['bbox'][1] + chunk[i]['bbox'][3]) / 2
            x_icon = chunk[i]['bbox'][0] - 11
            end = starts[si + 1][0] if si + 1 < len(starts) else len(body)
            parts = [first_text]
            for ln in body[i + 1:end]:
                if ln['bbox'][0] >= 370 or ln['text'].startswith(META_KEYS):
                    continue
                # export footers (link.testbook.com / cdn.digialm.com ...) sometimes land
                # inside the last option's line range — never part of the option text
                if 'http://' in ln['text'] or 'https://' in ln['text']:
                    continue
                parts.append(ln['text'])
            opts[n] = {'text': ' '.join(p for p in parts if p.strip()).strip(), 'x': x_icon, 'y': y}
        for n, o in opts.items():
            o['color'] = option_color(im, zoom, o['x'], o['y'])
            del o['x']; del o['y']

        possible_answer = re.search(r'Possible Answer:\s*(.*)', text)
        greens = [n for n, o in opts.items() if o['color'] == 'G']
        stem_m = re.match(r'^Q\.\d+\s*(.*?)\s*(?:Ans|Case Sensitivity)', text, re.S)
        stem = stem_m.group(1).strip() if stem_m else ''
        empty_stem = len(stem) < 3 or (opts and all(not o['text'].strip() for o in opts.values()))
        ambiguous = empty_stem or not (
            (len(opts) == 4 and len(greens) == 1) or (not opts and possible_answer))

        records.append({
            'page': pno + 1,
            'qno': qno,
            'section': section,
            'qtype': qtype.group(1) if qtype else None,
            'preamble': preamble if bi == 0 else '',
            'text': text,
            'opts': {n: o['text'] for n, o in opts.items()},
            'green': greens[0] if len(greens) == 1 else greens,
            'possible_answer': possible_answer.group(1).strip() if possible_answer else None,
            'ambiguous': ambiguous,
        })
    return records


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--first', type=int, default=1)
    ap.add_argument('--last', type=int, default=None)
    ap.add_argument('--dpi', type=int, default=150)
    ap.add_argument('--out', help='write full JSON draft here')
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    last = a.last or doc.page_count
    records = []
    for pno in range(a.first - 1, last):
        for rec in process_page(doc, pno, a.dpi):
            records.append(rec)
            flag = ' <-- AMBIGUOUS, VISION-CHECK' if rec['ambiguous'] else ''
            print(rec['page'], 'Q'+str(rec['qno']), rec['section'], rec['qtype'],
                  'green=', rec['green'], 'possible_answer=', rec['possible_answer'], flag)

    n_amb = sum(r['ambiguous'] for r in records)
    print(f'\n{len(records)} questions, {n_amb} ambiguous (need vision check)')

    if a.out:
        with open(a.out, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=1)
        print('wrote', a.out)


if __name__ == '__main__':
    main()
