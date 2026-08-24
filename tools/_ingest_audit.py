import pymupdf, json, re, sys, collections
S = r'C:/Users/GURANSH/AppData/Local/Temp/claude/c--Users-GURANSH-Desktop-percentile-99-percentile99/a29a52b4-2680-48f1-a548-fc3a533ca51e/scratchpad/ingest/new'
PAPERS = [('2024s1','2024-Slot-I'),('2024s2','2024-Slot-II'),('2024s3','2024-Slot-III'),
          ('2025s1','2025-Slot-I'),('2025s2','2025-Slot-II'),('2025s3','2025-Slot-III')]
def rules(pdf):
    d = pymupdf.open(pdf); out = collections.defaultdict(list)
    for p in range(d.page_count):
        for dr in d[p].get_drawings():
            r = dr['rect']
            # thin wide horizontal rule = radical overline or fraction bar.
            # exclude the wide TITA answer boxes (they are tall) and page rules.
            if r.height < 2.5 and 5 < r.width < 260:
                out[p+1].append(r.y0)
    return out
def audit(tag, slot):
    rr = rules('papers/Actual-CAT-%s.pdf' % slot)
    d = json.load(open('%s/%s.json' % (S, tag), encoding='utf-8'))
    flags = {}
    for r in d['questions']:
        why = []
        blob = r['head'] + ' || ' + ' | '.join(r['opts'].values())
        if '\ufffd' in blob or re.search(r'[\uf000-\uf8ff]', blob): why.append('glyph')
        if re.search(r'\S {3,}\S', blob): why.append('gappy')
        if r['type'] == 'mcq' and (len(r['opts']) != 4 or any(not v.strip() for v in r['opts'].values())):
            why.append('opts')
        if not r['head'].strip(): why.append('stem')
        for pg, (lo, hi) in r.get('extent', {}).items():
            if any(lo - 4 <= y <= hi + 14 for y in rr.get(int(pg), [])):
                why.append('rule'); break
        if why: flags[r['n']] = ','.join(sorted(set(why)))
    return flags
tot = 0
for tag, slot in PAPERS:
    f = audit(tag, slot); tot += len(f)
    print('%-8s %2d  %s' % (tag, len(f), f))
print('TOTAL needing review:', tot)
