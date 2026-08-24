#!/usr/bin/env python3
"""
Draft extractor for the UNSOLVED "testbook.com Previous Year Paper" PDFs
(CAT 2018 / 2019 here): questions flow linearly as

    Section : Verbal Ability
    DIRECTIONS for the question: ...
    Question No. : 1
    <passage, only on the first question of a group>
    <stem>
    A) ...  B) ...  C) ...  D) ...

and the answer key lives in one block at the end as

    QNo:-  1  ,Correct Answer:-  C

MCQ keys are letters A-D; anything else (a number, a word) is a TITA answer.
This is framework format "B" — see docs/INGEST_FRAMEWORK.md §3/§4.

Produces a per-question DRAFT for review; it is NOT a mocks.json writer. The
passage/DILR-set text that opens a group is left attached to that group's first
question as `head` — split it into ctxs by hand (the boundary between a passage
and the stem that follows it is a judgement call, not a reliable pattern).

Usage:
    python tools/extract_pyq_paper.py paper.pdf --out draft.json
"""
import argparse
import json
import re
import pymupdf

Q_RE = re.compile(r'^Question No\.?\s*:\s*(\d+)\s*$')
SEC_RE = re.compile(r'^Section\s*:\s*(.+?)\s*$')
OPT_RE = re.compile(r'^([A-D])\)\s*(.*)$')
KEY_RE = re.compile(r'QNo:-\s*(\d+)\s*,\s*Correct Answer:-\s*(.+?)\s*$')
DIR_RE = re.compile(r'^DIRECTIONS?\s+for\s+the\s+question', re.I)
DROP_RE = re.compile(r'^(https?://|Page\s*-\s*\d+|Download Testbook App|testbook\.com)')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# Adobe Symbol font, as used by the 2024/2025 papers for maths operators. The glyphs
# arrive as private-use codepoints (0xF000 + Symbol code) and would otherwise come out
# as replacement boxes, so map the ones these papers actually use to real Unicode.
SYMBOL_MAP = {
    0x28: '(', 0x29: ')', 0x2B: '+', 0x2D: '−', 0x3D: '=', 0x3E: '>',
    0x3C: '<', 0x5B: '[', 0x5D: ']', 0x44: 'Δ', 0x61: 'α', 0x62: 'β',
    0x64: 'δ', 0x70: 'π', 0x71: 'θ', 0x6C: 'λ', 0x6D: 'μ',
    0x53: 'Σ', 0x57: 'Ω', 0xA3: '≤', 0xA5: '∞', 0xB0: '°',
    0xB1: '±', 0xB3: '≥', 0xB4: '×', 0xB7: '⋅', 0xB8: '÷',
    0xB9: '≠', 0xBB: '≈', 0xBC: '…', 0xC7: '∩', 0xC8: '∪',
    0xCC: '⊂', 0xCE: '∈', 0xD0: '∠', 0xD6: '√', 0x2A: '∗',
    0x24: '∃', 0x40: '≅', 0xAE: '→',
}
# pieces of multi-line (stacked) parentheses and brackets — their presence means the
# expression is laid out across lines and needs a human look, so mark it visibly
STACK_CODES = set(range(0xE6, 0xEC)) | set(range(0xF6, 0xFC))


def map_symbol(text):
    out = []
    for ch in text:
        o = ord(ch)
        if 0xF000 <= o <= 0xF0FF:
            code = o - 0xF000
            if code in SYMBOL_MAP:
                out.append(SYMBOL_MAP[code])
                continue
            if code in STACK_CODES:
                continue          # drop the bracket-fragment glyphs themselves
            out.append('�')  # unmapped: leave a marker so the audit catches it
            continue
        out.append(ch)
    return ''.join(out)


def line_html(line):
    """Rebuild a line as HTML, restoring the exponents/indices the plain text layer
    throws away. This PDF sets them as smaller spans on a shifted baseline: raised
    (smaller origin y) => superscript, dropped => subscript. Without this, "x2018y2017"
    and "log2(5 + log3 a)" come out as ambiguous digit soup."""
    spans = [s for s in line['spans'] if s['text']]
    if not spans:
        return ''
    # Base size is the size covering the most characters, NOT the largest: option
    # labels ("A) ") are set a point larger than the body, so max() would make the
    # body itself look raised and wrap ordinary words in <sup>.
    weight = {}
    for s in spans:
        weight[s['size']] = weight.get(s['size'], 0) + len(s['text'])
    base_size = max(weight, key=weight.get)
    base_oy = next(s['origin'][1] for s in spans if s['size'] == base_size)
    # A raised/dropped baseline is proportional to the type size, not an absolute
    # number of points: 11pt body text shifts its subscripts by under a point, which
    # a fixed threshold misses entirely.
    shift = max(0.35, base_size * 0.04)
    parts = []
    for s in spans:
        t = esc(map_symbol(s['text']))
        if s['size'] < base_size * 0.92 and t.strip():
            dy = s['origin'][1] - base_oy
            if dy < -shift:
                parts.append('<sup>' + t.strip() + '</sup>')
                continue
            if dy > shift:
                parts.append('<sub>' + t.strip() + '</sub>')
                continue
        parts.append(t)
    return ''.join(parts).strip()


def page_lines(page, paras=True):
    """Lines in reading order. With paras=True, insert an empty string wherever the
    vertical gap jumps — that restores paragraph breaks, which is what makes the
    passage-vs-stem boundary recoverable later. Text comes back HTML-escaped with
    <sup>/<sub> already applied, so callers must NOT escape it again."""
    out = []
    for b in page.get_text('dict')['blocks']:
        if b.get('type') != 0:
            continue
        for l in b['lines']:
            txt = line_html(l)
            if txt:
                out.append({'y0': l['bbox'][1], 'y1': l['bbox'][3],
                            'x': l['bbox'][0], 'text': txt})
    out.sort(key=lambda l: (round(l['y0'], 1), l['x']))
    if not paras or len(out) < 2:
        return [l['text'] for l in out]
    gaps = sorted(b['y0'] - a['y1'] for a, b in zip(out, out[1:]))
    typical = gaps[len(gaps) // 2]
    res = []
    for k, l in enumerate(out):
        if k and (l['y0'] - out[k - 1]['y1']) > typical + 4:
            res.append('')
        res.append(l['text'])
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('--out')
    a = ap.parse_args()

    doc = pymupdf.open(a.pdf)
    lines = []
    for pno in range(doc.page_count):
        for t in page_lines(doc[pno]):
            if not DROP_RE.match(t):
                lines.append(t)
    # collapse runs of blanks left behind by dropped header/footer lines
    lines = [t for i, t in enumerate(lines) if t or (i and lines[i - 1])]

    # everything from the first key line on is the answer key + explanations
    first_key = next((i for i, t in enumerate(lines) if KEY_RE.search(t)), len(lines))
    body, keytext = lines[:first_key], lines[first_key:]

    keys = {}
    for t in keytext:
        m = KEY_RE.search(t)
        if m:
            keys[int(m.group(1))] = m.group(2).strip()

    # split the body into question blocks, tracking the current section
    starts = [i for i, t in enumerate(body) if Q_RE.match(t)]
    recs = []
    for si, i in enumerate(starts):
        qno = int(Q_RE.match(body[i]).group(1))
        end = starts[si + 1] if si + 1 < len(starts) else len(body)
        chunk = body[i + 1:end]
        sec = None
        for t in body[:i]:
            m = SEC_RE.match(t)
            if m:
                # section names are labels, not content — undo the HTML escaping
                sec = m.group(1).replace('&amp;', '&')
        # a "DIRECTIONS ..." line just before this question opens a new group
        directions = None
        for t in reversed(body[max(0, i - 4):i]):
            if DIR_RE.match(t):
                directions = t
                break

        # The option block starts at the first line beginning with "A)". Options are
        # NOT one per line — this paper prints them two or four to a line — so slice
        # the block by locating the A)/B)/C)/D) markers in order. Sorting the markers
        # that were actually found keeps the slices right even when one is missing
        # (the source PDF does drop an option at a page break now and then).
        first_a = next((j for j, t in enumerate(chunk) if t.startswith('A)')), None)
        opts = {}
        if first_a is None:
            head = chunk
        else:
            head = chunk[:first_a]
            # the next question's DIRECTIONS line sits inside this chunk — it is not
            # part of the last option
            opt_end = next((j for j in range(first_a, len(chunk))
                            if DIR_RE.match(chunk[j])), len(chunk))
            blob = ' '.join(t for t in chunk[first_a:opt_end] if t)
            found, pos = [], 0
            for L in 'ABCD':
                i = blob.find(L + ')', pos)
                if i >= 0:
                    found.append((i, L))
                    pos = i + 2
            found.sort()
            for k, (i, L) in enumerate(found):
                stop = found[k + 1][0] if k + 1 < len(found) else len(blob)
                opts[L] = blob[i + 2:stop].strip()

        key = keys.get(qno)
        is_mcq = bool(key) and key.upper() in ('A', 'B', 'C', 'D')
        recs.append({
            'n': qno,
            'section': sec,
            'directions': directions,
            'type': 'mcq' if is_mcq else 'tita',
            'head': '\n'.join(head),          # passage/set text + stem, needs manual split
            'opts': opts,
            'key': key,
            'ans': 'ABCD'.index(key.upper()) if is_mcq else key,
        })

    bad = [r['n'] for r in recs if r['key'] is None
           or (r['type'] == 'mcq' and len(r['opts']) != 4)]
    print(f'{len(recs)} questions | {len(keys)} answer keys')
    for s in sorted({r['section'] for r in recs if r['section']}):
        print('  section:', s, '->', sum(1 for r in recs if r['section'] == s))
    print('  mcq:', sum(1 for r in recs if r['type'] == 'mcq'),
          '| tita:', sum(1 for r in recs if r['type'] == 'tita'))
    if bad:
        print('  NEEDS REVIEW (missing key / not 4 options):', bad)

    if a.out:
        json.dump(recs, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('wrote', a.out)


if __name__ == '__main__':
    main()
