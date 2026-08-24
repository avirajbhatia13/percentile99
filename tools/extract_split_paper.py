#!/usr/bin/env python3
"""
Draft extractor for the "Actual CAT <year> Slot - N" PDFs where the question paper
and the answer key are SEPARATE files (CAT 2024 and 2025 here).

Question paper layout:

    SECTION: VERBAL ABILITY AND READING COMPREHENSION
    DIRECTIONS for questions 1 to 4: The passage below is accompanied by ...
    <shared passage / DILR set text>
    1.
    <stem>
    A. ...   (2024)      or      1. ...   (2025)
    B. ...                       2. ...

Two things make this format easy and one makes it fiddly.

Easy: the DIRECTIONS line states its own question range, so passage/DILR-set
grouping is read straight off the paper instead of being inferred from paragraph
counts. Groups come back in the draft as `groups`. And the answer key is a
separate file, so no green-tick detection is needed at all.

Fiddly: the 2025 papers label options "1." to "4.", which collides with question
numbers, and their jumbled-sentence stems contain numbered lists too. Question
markers are distinguished by sitting in the left margin (x < 70) while options and
list items are indented; and options are only looked for when the answer key says
the question is an MCQ.

Answer-key dialects, auto-detected:
  * 2024 — MCQ keys are letters A-D; a bare number means TITA.
  * 2025 — MCQ keys are option NUMBERS 1-4; TITA rows are tagged "50 (TITA)".

Usage:
    python tools/extract_split_paper.py paper.pdf key.pdf --out draft.json
"""
import argparse
import json
import re
import pymupdf

from extract_pyq_paper import line_html   # shared <sup>/<sub> restoration

SEC_RE = re.compile(r'^SECTION\s*[:\-]\s*(.+?)\s*$', re.I)
DIR_RE = re.compile(r'^DIRECTIONS?\s+for\s+(?:questions?|the\s+question)\s*'
                    r'(\d+)?\s*(?:(?:to|&|and|,|-|–|—)\s*(\d+))?', re.I)
LBL_RE = re.compile(r'^([A-D]|\d{1,2})[\.\)]\s*(.*)$', re.S)
TITA_RE = re.compile(r'^(.*?)\s*\(\s*TITA\s*\)\s*$', re.I)
DROP_RE = re.compile(r'^(Actual\s+CAT\b|Slot\s*[-–]|Answer\s+Key\b|Explanation\b|'
                     r'Q\.\s*No\b|Key$|\d{1,3}$|Page\s*\d+)', re.I)
QMARK_MAX_X = 70          # question numbers sit in the left margin


def lines_of(pdf):
    doc = pymupdf.open(pdf)
    out = []
    for pno in range(doc.page_count):
        for b in doc[pno].get_text('dict')['blocks']:
            if b.get('type') != 0:
                continue
            for l in b['lines']:
                t = line_html(l)
                if t:
                    out.append({'text': t, 'y': l['bbox'][1], 'x': l['bbox'][0],
                                'page': pno + 1})
    return out


def rows_by_line(rows, tol=6.0):
    """Cluster lines into visual rows by y, then order each row left-to-right.

    Both files need this. In the key file the three "Q. No" cells of a row are
    emitted before the three "Key" cells, so a plain y-then-x sort would pair a
    question number with the wrong answer. In the paper a question marker and the
    first line of its stem share a visual line but can differ by a fraction of a
    point, which would otherwise put the stem before its own marker."""
    out, cur = [], []
    for r in sorted(rows, key=lambda r: (r['page'], r['y'])):
        if cur and (r['page'] != cur[-1]['page'] or abs(r['y'] - cur[-1]['y']) > tol):
            out.append(sorted(cur, key=lambda r: r['x']))
            cur = []
        cur.append(r)
    if cur:
        out.append(sorted(cur, key=lambda r: r['x']))
    return out


def parse_keys(pdf):
    """Answer-key table -> {qno: raw key text}. Stops at the explanations below it."""
    keys = {}
    for row in rows_by_line(lines_of(pdf)):
        cells = [r['text'].strip() for r in row]
        if any(re.match(r'^Explanation\b', c, re.I) for c in cells):
            break
        for i, c in enumerate(cells):
            m = re.fullmatch(r'(\d{1,3})\.', c)
            if not m or i + 1 >= len(cells):
                continue
            v = cells[i + 1].strip()
            if re.fullmatch(r'[A-D]', v, re.I) or TITA_RE.match(v) \
                    or re.fullmatch(r'-?\d+(?:\.\d+)?', v):
                keys[int(m.group(1))] = v
    return keys


def resolve_keys(raw):
    """Turn raw key text into (type, answer), honouring the file's dialect.

    A file that tags rows "(TITA)" is the 2025 style, where an untagged 1-4 is an
    MCQ option number. Otherwise it is the 2024 style, where letters are MCQs and a
    bare number is a TITA answer."""
    tita_style = any(TITA_RE.match(v) for v in raw.values())
    out = {}
    for n, v in raw.items():
        v = v.strip()
        m = TITA_RE.match(v)
        if m:
            out[n] = ('tita', m.group(1).strip())
            continue
        if re.fullmatch(r'[A-D]', v, re.I):
            out[n] = ('mcq', 'ABCD'.index(v.upper()))
            continue
        if tita_style and re.fullmatch(r'[1-4]', v):
            out[n] = ('mcq', int(v) - 1)
            continue
        out[n] = ('tita', v)
    return out


def split_stem_opts(cells, is_mcq):
    """Split a question's cells into stem text and options.

    TITA questions have no options at all, so a numbered list inside the stem (the
    jumbled-sentence questions) stays in the stem. For an MCQ, take the LAST complete
    run of labels — A,B,C,D or 1,2,3,4 — so a numbered list earlier in the stem is
    not mistaken for the options."""
    if not is_mcq:
        return [c['text'] for c in cells], {}

    for wanted in (list('ABCD'), list('1234')):
        runs, cur, pos = [], {}, 0
        for i, c in enumerate(cells):
            m = LBL_RE.match(c['text'].strip())
            if m and m.group(1).upper() == wanted[pos]:
                cur[wanted[pos]] = i
                pos += 1
                if pos == 4:
                    runs.append(cur)
                    cur, pos = {}, 0
        if runs:
            run = runs[-1]
            first = run[wanted[0]]
            opts = {}
            for k, letter in enumerate(wanted):
                start = run[letter]
                end = run[wanted[k + 1]] if k + 1 < 4 else len(cells)
                body = LBL_RE.match(cells[start]['text'].strip()).group(2)
                extra = [cells[j]['text'] for j in range(start + 1, end)]
                opts['ABCD'[k]] = ' '.join([body] + extra).strip()
            return [c['text'] for c in cells[:first]], opts
    return [c['text'] for c in cells], {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paper')
    ap.add_argument('key')
    ap.add_argument('--out')
    a = ap.parse_args()

    resolved = resolve_keys(parse_keys(a.key))
    total = max(resolved) if resolved else 0

    rows = [r for r in lines_of(a.paper) if not DROP_RE.match(r['text'].strip())]
    cells = [c for row in rows_by_line(rows) for c in row]

    # ---- pass 1: locate section headers, DIRECTIONS blocks and question markers ----
    marks, sec_at, dirs = [], {}, []
    section, pend = None, None
    expect = 1
    for i, c in enumerate(cells):
        t = c['text'].strip()
        m = SEC_RE.match(t)
        if m:
            sec_at[i] = m.group(1).replace('&amp;', '&')
            continue
        if pend is not None and not pend['done']:
            tight = (c['page'] == pend['page'] and 0 <= c['y'] - pend['y'] < 16)
            if tight and not re.search(r'[.?!:]\s*$', pend['text']):
                pend['text'] += ' ' + t
                pend['y'] = c['y']
                pend['upto'] = i
                continue
            pend['done'] = True
        m = DIR_RE.match(t)
        if m:
            lo = int(m.group(1)) if m.group(1) else None
            hi = int(m.group(2)) if m.group(2) else lo
            pend = {'first': lo, 'last': hi, 'text': t, 'at': i, 'upto': i,
                    'page': c['page'], 'y': c['y'],
                    'done': bool(re.search(r'[.?!]\s*$', t))}
            dirs.append(pend)
            continue
        m = LBL_RE.match(t)
        if m and c['x'] < QMARK_MAX_X and m.group(1).isdigit() \
                and int(m.group(1)) == expect and expect <= total:
            marks.append({'n': expect, 'at': i, 'inline': m.group(2).strip()})
            expect += 1

    # ---- pass 2: slice per question, and read each DIRECTIONS block's context ----
    recs = []
    dir_at = sorted(d['at'] for d in dirs)
    for k, mk in enumerate(marks):
        end = marks[k + 1]['at'] if k + 1 < len(marks) else len(cells)
        # the DIRECTIONS block introducing the NEXT group sits between two question
        # markers — it belongs to neither, so stop this question short of it
        nd = next((i for i in dir_at if mk['at'] < i < end), None)
        if nd is not None:
            end = nd
        body = cells[mk['at'] + 1:end]
        sec = None
        for i, s in sec_at.items():
            if i < mk['at']:
                sec = s
        typ, ans = resolved.get(mk['n'], (None, None))
        stem, opts = split_stem_opts(body, typ == 'mcq')
        if mk['inline']:
            stem = [mk['inline']] + stem
        # vertical extent of the question, per page — lets an audit ask whether a
        # drawn rule (a radical overline or a fraction bar, neither of which exists
        # in the text layer) falls inside this question
        spans = {}
        for c in cells[mk['at']:end]:
            lo, hi = spans.get(c['page'], (c['y'], c['y']))
            spans[c['page']] = (min(lo, c['y']), max(hi, c['y']))
        gov = None
        for d in dirs:
            if d['at'] < mk['at']:
                gov = d['text']
        recs.append({'n': mk['n'], 'section': sec, 'type': typ or 'tita',
                     'directions': gov,
                     'head': '\n'.join(stem).strip(), 'opts': opts,
                     'ans': ans, 'page': cells[mk['at']]['page'],
                     'extent': {str(k): v for k, v in spans.items()}})

    at_of = {mk['n']: mk['at'] for mk in marks}
    groups = []
    for d in dirs:
        first = d['first']
        if first is None:
            nxt = next((mk['n'] for mk in marks if mk['at'] > d['at']), None)
            first = nxt
        if first is None or first not in at_of:
            continue
        ctx = [c['text'] for c in cells[d['upto'] + 1:at_of[first]]]
        ctx = [t for t in ctx if t.strip()]
        if ctx:
            groups.append({'first': first, 'last': d['last'] or first,
                           'ctx': '<br>'.join(ctx)})

    bad = [r['n'] for r in recs if r['ans'] is None or not r['head'].strip()
           or (r['type'] == 'mcq' and (len(r['opts']) != 4
               or any(not v.strip() for v in r['opts'].values())))]
    print(f'{len(recs)} questions | {len(resolved)} keys | {len(groups)} grouped contexts')
    for s in sorted({r['section'] for r in recs if r['section']}):
        print('  section:', s, '->', sum(1 for r in recs if r['section'] == s))
    print('  mcq:', sum(1 for r in recs if r['type'] == 'mcq'),
          '| tita:', sum(1 for r in recs if r['type'] == 'tita'))
    missing = [n for n in range(1, total + 1) if n not in {r['n'] for r in recs}]
    if missing:
        print('  MISSING QUESTIONS:', missing)
    if bad:
        print('  NEEDS REVIEW:', bad)

    if a.out:
        json.dump({'questions': recs, 'groups': groups},
                  open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', a.out)


if __name__ == '__main__':
    main()
