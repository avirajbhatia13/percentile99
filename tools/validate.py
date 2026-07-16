#!/usr/bin/env python3
"""
Schema + topic-tag validator for mocks.json. Run after adding/editing a mock.

    python3 tools/validate.py            # validate whole file
    python3 tools/validate.py cat2023slot1   # validate one mock id

Exits non-zero if any problem is found. Zero output problems == good to commit.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOCKS = os.path.join(ROOT, 'mocks.json')
INDEX = os.path.join(ROOT, 'index.html')


def valid_subs():
    """Fine-grained QA/LRDI subs declared in index.html's DATA.subs (for a soft check)."""
    try:
        html = open(INDEX, encoding='utf-8').read()
        m = re.search(r'"subs":(\[\[.*?\]\])', html)
        return set(s for _, s in json.loads(m.group(1)))
    except Exception:
        return set()


def main():
    data = json.load(open(MOCKS, encoding='utf-8'))
    only = sys.argv[1] if len(sys.argv) > 1 else None
    subs_known = valid_subs()
    problems = 0
    figs_missing = 0
    ids = set()
    for mk in data:
        if only and mk['id'] != only:
            continue
        if mk['id'] in ids:
            print('DUP id', mk['id']); problems += 1
        ids.add(mk['id'])
        for key in ('id', 'name', 'year', 'secMin', 'ctxs', 'sections'):
            if key not in mk:
                print(mk.get('id', '?'), 'missing', key); problems += 1
        nctx = len(mk.get('ctxs', []))
        # figure references exist on disk
        blob = ' '.join(mk.get('ctxs', [])) + ' '.join(
            q.get('q', '') for s in mk['sections'] for q in s['qs'])
        for src in set(re.findall(r'src="([^"]+)"', blob)):
            if not os.path.exists(os.path.join(ROOT, src)):
                print(mk['id'], 'FIGURE MISSING', src); figs_missing += 1; problems += 1
        for s in mk['sections']:
            for q in s['qs']:
                tag = f"{mk['id']}/{s['name']}/Q{q.get('n')}"
                if q.get('type') not in ('mcq', 'tita'):
                    print(tag, 'bad type', q.get('type')); problems += 1
                if q.get('type') == 'mcq':
                    if not (isinstance(q.get('ans'), int) and 0 <= q['ans'] < 4):
                        print(tag, 'mcq ans not int 0..3:', q.get('ans')); problems += 1
                    if len(q.get('opts', [])) != 4 or not all(str(o).strip() for o in q.get('opts', [])):
                        print(tag, 'mcq needs 4 non-empty opts:', q.get('opts')); problems += 1
                else:
                    if not isinstance(q.get('ans'), str):
                        print(tag, 'tita ans not string:', q.get('ans')); problems += 1
                c = q.get('c')
                if c is not None and not (isinstance(c, int) and 0 <= c < nctx):
                    print(tag, 'bad ctx index', c, 'of', nctx); problems += 1
                if not q.get('sub'):
                    print(tag, 'MISSING sub (topic)'); problems += 1
                elif s['name'] == 'QA' and subs_known and q['sub'] not in subs_known:
                    print(tag, 'note: QA sub not in DATA.subs taxonomy:', q['sub'])  # soft
    total = sum(len(s['qs']) for mk in data for s in mk['sections'] if not only or mk['id'] == only)
    print(f'\n{"OK" if problems == 0 else "PROBLEMS: %d" % problems} — '
          f'{len(ids)} mock(s), {total} questions checked'
          + (f', {figs_missing} figures missing' if figs_missing else ''))
    sys.exit(1 if problems else 0)


if __name__ == '__main__':
    main()
