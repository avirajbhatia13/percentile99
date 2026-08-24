# -*- coding: utf-8 -*-
"""Assemble one split-format paper (CAT 2024 / 2025) into mocks.json.

    python build_split.py 2024s1 cat2024slot1 "CAT 2024 Slot 1" 2024

Reads the extractor's draft plus a per-paper overrides module `ov_<tag>.py`, and
takes topic tags from tools/suggest_topics.py with the DILR sets named by hand
(one bucket per set, per INGEST_NOTES.md)."""
import sys, os, ast, subprocess, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from lib_build import load_split, split_html, q_split, append_mock

TOOLS = r'c:\Users\GURANSH\Desktop\percentile 99\percentile99\tools\suggest_topics.py'
tag, mock_id, name, year = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
ov = importlib.import_module('ov_' + tag)

byn, groups = load_split(os.path.join(HERE, tag + '.json'))

raw = subprocess.run([sys.executable, TOOLS, os.path.join(HERE, tag + '.json')],
                     capture_output=True, text=True, encoding='utf-8').stdout
tags = ast.literal_eval(raw[raw.index('{'):raw.rindex('}') + 1])
tags.update(getattr(ov, 'TAGS', {}))
for (lo, hi), topic in ov.DILR_SETS.items():          # DILR: one bucket per set
    for n in range(lo, hi + 1):
        tags[n] = topic
missing = [n for n, t in tags.items() if t == '?']
assert not missing, 'unresolved topics: %s' % missing

FIG = ('<div class="qfig"><img loading="lazy" src="img/pyq/%s/%s/%s" alt="%s"></div>')
year_dir, slot_dir = str(year), 's' + mock_id[-1]

ctxs, ctx_of = [], {}
for g in groups:
    body = '<br>'.join(l for l in g['ctx'].split('<br>') if l.strip())
    key = (g['first'], g['last'])
    if key in getattr(ov, 'FIGS', {}):
        fn, alt = ov.FIGS[key]
        body += FIG % (year_dir, slot_dir, fn, alt)
    if key in getattr(ov, 'CTX_FIX', {}):
        body = ov.CTX_FIX[key](body)
    ctxs.append(body)
    for n in range(g['first'], g['last'] + 1):
        ctx_of[n] = len(ctxs) - 1

buckets = {'VARC': [], 'DILR': [], 'QA': []}
for n in sorted(byn):
    rec = dict(byn[n])
    if n in getattr(ov, 'RETYPE', {}):
        rec['type'], rec['ans'] = ov.RETYPE[n]
    sec = (rec['section'] or '').upper()
    short = ('VARC' if sec.startswith('VERB') else
             'DILR' if sec.startswith(('DI', 'DATA')) else 'QA')
    buckets[short].append(q_split(rec, ctx_of.get(n), tags[n],
                                  stem=ov.STEM.get(n), opts=ov.OPTS.get(n)))

append_mock({"id": mock_id, "name": name, "year": year, "secMin": 40, "ctxs": ctxs,
             "sections": [{"name": s, "qs": buckets[s]} for s in ('VARC', 'DILR', 'QA')]})
