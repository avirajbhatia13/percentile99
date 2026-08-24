#!/usr/bin/env python3
"""
Suggest a topic tag for every question in a draft, so tagging becomes a review pass
instead of ~70 judgement calls per paper.

Tags come from the app's own vocabularies: QA subtopics are the `DATA.subs` list in
index.html, VARC is tagged by question type, and DILR by set bucket (INGEST_NOTES.md).
Matching is keyword-based and deliberately conservative — anything it is not
reasonably sure about comes back as "?" for a human to fill in, which is the whole
point: the output is a starting map to correct, not an answer to trust blindly.

Usage:
    python tools/suggest_topics.py draft.json                # split format
    python tools/suggest_topics.py draft.json --fmt pyq      # 2018/2019 format
"""
import argparse
import json
import re

# (topic, regex) — first match wins, so put the specific before the general
QA_RULES = [
    ("Logarithms", r'\blog\b|logarithm'),
    ("Indices & Surds", r'√|<sup>|surd|\bindices\b|square root|cube root'),
    ("Arithmetic Progression", r'arithmetic progression|\bA\.?P\.?\b'),
    ("Geometric Progression", r'geometric progression|\bG\.?P\.?\b'),
    ("Sequence & Series", r'sequence|series|\bsum of (?:the )?(?:first|all)\b'
                          r'|\+\s*…|\+\s*\.\.\.'),
    ("Permutations & Combinations", r'permutation|combination|arrangement|how many ways|number of ways'),
    ("Probability", r'probabilit'),
    ("Venn Diagrams", r'\bsets?\b.*\b(?:union|intersection)|at least one of|neither|only .* and .*\bboth\b|students who (?:play|like|study)'),
    ("Remainders", r'remainder|\bmodulo\b'),
    ("HCF & LCM", r'\bH\.?C\.?F\b|\bL\.?C\.?M\b|highest common|least common'),
    ("Factors", r'\bfactors?\b|divisor|divisible|prime'),
    ("Time Speed Distance", r'\bspeed\b|km/?h|kmph|\btrain\b|\bboat\b|stream|travel|journey|walks?|cyclist|overtake'),
    ("Time & Work", r'\bwork(?:ing|s|ed)?\b.*\bdays?\b|\bpipes?\b|\btank\b|\bcistern\b'
                    r'|complete the (?:task|job|work)|\bjob\b.*\bdays?\b|alone can do'),
    ("Alligation & Mixture", r'mixture|alligation|\bsolution\b.*\b(?:acid|milk|water|alcohol|salt)|replaced with'),
    ("Profit & Loss", r'profit|loss|discount|cost price|selling price|marked price|\bsells?\b|\bbought\b'),
    ("SI & CI", r'interest|compound|per annum|\bprincipal\b|invests?'),
    ("Percentages", r'percent|\b%\b|increase[sd]? by|decrease[sd]? by'),
    ("Averages", r'average|\bmean\b|\bmedian\b'),
    ("Ratio", r'\bratio\b|proportion'),
    ("Triangles", r'triangle|\bΔ\b|hypotenuse|equilateral|isosceles'),
    ("Circles", r'\bcircle\b|\bradius\b|\bdiameter\b|\bchord\b|\barc\b|circumference'),
    ("Quadrilaterals", r'rectangle|square\b|parallelogram|rhombus|trapez|quadrilateral'),
    ("Mensuration", r'\bvolume\b|surface area|\bcone\b|\bcylinder\b|\bsphere\b|\bcuboid\b|\bprism\b'),
    ("Functions", r'\bf\s*\(\s*x\s*\)|function|\bmin\s*\{|\bmax\s*\{'),
    ("Inequalities", r'inequalit|\b≤\b|\b≥\b|greater than or equal|less than or equal'),
    ("Quadratic Equations", r'quadratic|\broots?\b|x<sup>2</sup>|x\^2'),
    ("Simple Equations", r'\bequations?\b|\bsolve for\b'),
    ("Numbers Basics", r'\bdigits?\b|natural number|integer'),
]

VARC_RULES = [
    ("Para-jumble", r'four sentences.*sequenc|proper sequencing|coherent paragraph.*sequence'),
    ("Odd One Out", r'odd sentence|does not (?:fit|belong)|five sentences.*odd'
                    r'|[Ff]ive sentences related to a topic'),
    ("Para-summary", r'alternate summaries|four summaries|best captures the essence'
                     r'|most appropriate summary'),
    ("Para-completion", r'sentence that is missing|would best fit|best fits among the options'),
    ("Reading Comprehension", r'passage below is accompanied|based on the passage'
                              r'|read the passage'),
]

DILR_RULES = [
    ("Games & Tournaments", r'tournament|\bmatch(?:es)?\b|\bround\b.*\bplayed\b|\bteams?\b.*\bscore'),
    ("Networks & Routes", r'\broute\b|\bnetwork\b|intersection|\bstreet\b|\bcity\b.*\bconnected\b|shortest path'),
    ("Venn Diagrams & Set Theory", r'at least one of|exactly one of|\bboth\b.*\band\b.*\bnot\b|visited by'),
    ("Sequencing & Scheduling", r'\bschedule\b|\bslot\b|\btime\b.*\barriv|\bqueue\b|\border\b.*\bfinish'),
    ("Grid & Arrangements", r'\bgrid\b|\brows?\b.*\bcolumns?\b|\bseated\b|\barrang'),
    ("Selection & Distribution", r'\bdistribut|\ballocat|\bassign|\bselect'),
    ("Tables & Data Sets", r'\btable\b|\bchart\b|\bgraph\b|\bbar\b|\bpie\b|\bdata\b'),
    ("Conditional Logic & Puzzles", r'.'),          # fallback for DILR
]


def pick(rules, text):
    for topic, pat in rules:
        if re.search(pat, text, re.I):
            return topic
    return '?'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('draft')
    ap.add_argument('--fmt', choices=('split', 'pyq'), default='split')
    a = ap.parse_args()

    raw = json.load(open(a.draft, encoding='utf-8'))
    qs = raw['questions'] if a.fmt == 'split' else raw
    groups = raw.get('groups', []) if a.fmt == 'split' else []
    ctx_of = {}
    for g in groups:
        for n in range(g['first'], g['last'] + 1):
            ctx_of[n] = g['ctx']

    out = {}
    last_dir = ''
    for r in sorted(qs, key=lambda r: r['n']):
        n = r['n']
        sec = (r.get('section') or '').upper()
        body = r.get('head', '')
        # The DIRECTIONS line names a VARC question's type, but it is printed once
        # per group — the 2nd to 5th questions of a passage inherit it.
        if r.get('directions'):
            last_dir = r['directions']
        govern = last_dir + ' ' + body
        if sec.startswith('VERBAL'):
            t = pick(VARC_RULES, govern)
            # anything hanging off a real passage is comprehension unless it matched
            # one of the standalone types above
            if t == '?':
                # pyq drafts carry no groups; there a long head or an inherited
                # "Read the passage" direction is the comprehension signal
                long_ctx = len(ctx_of.get(n, '')) > 600
                passagey = re.search(r'read the passage', govern, re.I)
                t = "Reading Comprehension" if (long_ctx or passagey) else '?'
        elif sec.startswith(('DI', 'DATA')):
            t = pick(DILR_RULES, ctx_of.get(n, '') + ' ' + body)
        else:
            t = pick(QA_RULES, body)
        out[n] = t

    unknown = [n for n, t in out.items() if t == '?']
    print('{')
    for n in sorted(out):
        print('    %d: "%s",' % (n, out[n]))
    print('}')
    print('# unresolved (%d): %s' % (len(unknown), unknown))


if __name__ == '__main__':
    main()
