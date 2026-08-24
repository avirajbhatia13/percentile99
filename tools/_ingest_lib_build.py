# -*- coding: utf-8 -*-
"""Shared helpers: turn extract_response_sheet.py draft records into mocks.json shapes."""
import json
import re

MOCKS = r"c:\Users\GURANSH\Desktop\percentile 99\percentile99\mocks.json"

DROP_LINE = re.compile(
    r'^(https?://|\d{1,2}/\d{1,2}/\d{4},\s|Comprehension:|SubQuestion No\s*:|Section\s*:|Page \d+|'
    r'The passage below is accompanied by four questions\.|best answer for each question\.)')


def clean_ctx(preamble):
    """Strip export chrome from a captured preamble, keep the real passage/set text."""
    out = []
    for ln in preamble.split('\n'):
        s = ln.strip()
        if not s or DROP_LINE.match(s):
            continue
        out.append(s)
    return '<br>'.join(out)


def stem_of(text):
    """Question stem: everything between the Q.N marker and the answer block."""
    m = re.match(r'^Q\.\d+\s*(.*?)\s*(?:\nAns\b|Case Sensitivity)', text, re.S)
    s = m.group(1) if m else ''
    s = re.sub(r'\s*\n\s*', ' ', s).replace('​', '').strip()
    return s


def esc(s):
    """Escape bare & and < > that aren't already entities (app renders these as HTML)."""
    s = re.sub(r'&(?!#?\w+;)', '&amp;', s)
    s = s.replace('<', '&lt;').replace('>', '&gt;')
    return s


def load(draft):
    recs = [r for r in json.load(open(draft, encoding='utf-8')) if r['qno'] is not None]
    return {(r['page'], r['qno']): r for r in recs}, recs


def build_q(rec, n, c, sub, stem=None, opts=None, ans=None):
    """One question object. stem/opts/ans override the draft (for image-only math)."""
    q = stem if stem is not None else esc(stem_of(rec['text']))
    if rec['qtype'] == 'SA':
        a = ans if ans is not None else rec['possible_answer']
        assert isinstance(a, str) and a, f'bad tita ans {rec["page"]}/{rec["qno"]}'
        return {"n": n, "c": c, "type": "tita", "q": q, "opts": [], "ans": a, "sol": "", "sub": sub}
    o = opts if opts is not None else [esc(rec['opts'][k]) for k in ('1', '2', '3', '4')]
    a = ans if ans is not None else rec['green']
    assert isinstance(a, int) and 1 <= a <= 4, f'bad mcq ans {rec["page"]}/{rec["qno"]}: {a}'
    assert len(o) == 4 and all(str(x).strip() for x in o), f'bad opts {rec["page"]}/{rec["qno"]}'
    return {"n": n, "c": c, "type": "mcq", "q": q, "opts": o, "ans": a - 1, "sol": "", "sub": sub}


def append_mock(mock):
    data = json.load(open(MOCKS, encoding='utf-8'))
    assert not any(m['id'] == mock['id'] for m in data), 'duplicate id ' + mock['id']
    data.append(mock)
    json.dump(data, open(MOCKS, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    n = sum(len(s['qs']) for s in mock['sections'])
    print('appended', mock['id'], '| sections',
          [(s['name'], len(s['qs'])) for s in mock['sections']], '| total', n,
          '| mocks now', len(data))


# ---------- helpers for the 2018/2019 "Previous Year Paper" format ----------
# extract_pyq_paper.py already returns HTML-escaped text with <sup>/<sub> applied,
# so nothing here may call esc() again.

def load_pyq(path):
    return {r['n']: r for r in json.load(open(path, encoding='utf-8'))}


def paras(rec):
    return [p.strip() for p in rec['head'].split('\n\n') if p.strip()]


def html(ps):
    """Paragraph list -> HTML: lines joined by <br>, paragraphs by a blank line."""
    return '<br><br>'.join('<br>'.join(l for l in p.split('\n') if l.strip()) for p in ps)


def group(byn, first, last, ctx_paras):
    """Split a passage/DILR-set group into its shared context and per-question stems.

    Some groups repeat the whole context inside every question, others print it only
    on the first — detect by comparing the opening paragraph, then drop the context
    paragraphs from any question that repeats them."""
    lead = paras(byn[first])
    assert len(lead) > ctx_paras, f'group {first}: ctx_paras {ctx_paras} >= {len(lead)} paras'
    ctx = lead[:ctx_paras]
    stems = {}
    for n in range(first, last + 1):
        ps = paras(byn[n])
        repeats = len(ps) > ctx_paras and ps[0].strip() == lead[0].strip()
        stems[n] = ps[ctx_paras:] if repeats else ps
        assert stems[n], f'Q{n}: empty stem after splitting off context'
    return html(ctx), stems


def q_pyq(rec, n, c, sub, stem=None, opts=None):
    """One question object from a pyq draft record (answers come from the paper's key)."""
    q = stem if stem is not None else html(paras(rec))
    assert q.strip(), f'Q{rec["n"]}: empty stem'
    if rec['type'] == 'tita':
        assert isinstance(rec['ans'], str) and rec['ans'].strip(), f'Q{rec["n"]}: bad tita ans'
        return {"n": n, "c": c, "type": "tita", "q": q, "opts": [],
                "ans": rec['ans'].strip(), "sol": "", "sub": sub}
    o = opts if opts is not None else [rec['opts'].get(k, '') for k in 'ABCD']
    assert len(o) == 4 and all(str(x).strip() for x in o), f'Q{rec["n"]}: bad opts {o}'
    assert isinstance(rec['ans'], int) and 0 <= rec['ans'] <= 3, f'Q{rec["n"]}: bad mcq ans'
    return {"n": n, "c": c, "type": "mcq", "q": q, "opts": o,
            "ans": rec['ans'], "sol": "", "sub": sub}


# ---------- helpers for the split paper/key format (2024, 2025) ----------
# extract_split_paper.py returns HTML-escaped text with <sup>/<sub> applied, so
# nothing here may escape it again.

def load_split(path):
    d = json.load(open(path, encoding='utf-8'))
    return {r['n']: r for r in d['questions']}, d['groups']


def split_html(head):
    return '<br>'.join(l for l in head.split('\n') if l.strip())


def q_split(rec, c, sub, stem=None, opts=None, ans=None):
    """One question object from a split-format draft record."""
    q = stem if stem is not None else split_html(rec['head'])
    assert q.strip(), f'Q{rec["n"]}: empty stem'
    a = rec['ans'] if ans is None else ans
    if rec['type'] == 'tita':
        assert isinstance(a, str) and a.strip(), f'Q{rec["n"]}: bad tita ans {a!r}'
        return {"n": rec['n'], "c": c, "type": "tita", "q": q, "opts": [],
                "ans": a.strip(), "sol": "", "sub": sub}
    o = opts if opts is not None else [rec['opts'].get(k, '') for k in 'ABCD']
    assert len(o) == 4 and all(str(x).strip() for x in o), f'Q{rec["n"]}: bad opts {o}'
    assert isinstance(a, int) and 0 <= a <= 3, f'Q{rec["n"]}: bad mcq ans {a!r}'
    return {"n": rec['n'], "c": c, "type": "mcq", "q": q, "opts": o,
            "ans": a, "sol": "", "sub": sub}


def build_split(mock_id, name, year, byn, groups, tags, ctx_fix=None,
                stems=None, opts=None, sec_names=(('VERBAL', 'VARC'),
                                                  ('DI', 'DILR'), ('QUANT', 'QA'))):
    """Assemble a whole mock. `groups` come from the extractor's DIRECTIONS ranges,
    so each question's ctx index is derived, not hand-listed. `tags` maps qno->topic.
    `ctx_fix` may rewrite a context by its (first,last) range key."""
    stems, opts = stems or {}, opts or {}
    ctxs, ctx_of = [], {}
    for g in groups:
        html_ctx = '<br>'.join(l for l in g['ctx'].split('<br>') if l.strip())
        if ctx_fix and (g['first'], g['last']) in ctx_fix:
            html_ctx = ctx_fix[(g['first'], g['last'])](html_ctx)
        ctxs.append(html_ctx)
        for n in range(g['first'], g['last'] + 1):
            ctx_of[n] = len(ctxs) - 1

    buckets = {short: [] for _, short in sec_names}
    for n in sorted(byn):
        rec = byn[n]
        short = next((s for key, s in sec_names if (rec['section'] or '').upper().startswith(key)), None)
        assert short, f'Q{n}: unmapped section {rec["section"]!r}'
        assert n in tags, f'Q{n}: no topic tag'
        buckets[short].append(q_split(rec, ctx_of.get(n), tags[n],
                                      stem=stems.get(n), opts=opts.get(n)))
    append_mock({"id": mock_id, "name": name, "year": year, "secMin": 40,
                 "ctxs": ctxs,
                 "sections": [{"name": s, "qs": buckets[s]} for _, s in sec_names]})
