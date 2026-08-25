# -*- coding: utf-8 -*-
"""CAT 2025 Slot III — overrides.

Source defects:
1. The RC DIRECTION line for Q21-24 uses an ampersand ("questions 21 & 24")
   instead of "to"/"-", which the extractor's range parser reads as a single
   endpoint, leaving the group registered as (21, 21). GROUP_RANGE_FIX widens
   it to (21, 24); each question already carries the right text individually.
2. Similarly Q25-28's DIRECTION line prints "25-29" — one past its real end —
   so its context grouping key comes out (25, 29) even though only Q25-28
   share that passage; Q29 belongs to the next set ("questions 29-33"), which
   is itself correctly ranged and, being processed after, naturally
   overwrites Q29's context assignment. No fix needed for Q29 itself, but
   DILR_SETS/TAGS use the real (25, 28) range rather than the raw group key.
3. Two DILR tables (the friend call-minutes table for Q25-28, and the
   Passing-the-Buck round table for Q43-46) have their numeric/round-number
   cells dropped by the text layer, leaving only row/column labels. Both
   rebuilt by hand from the rendered page image via CTX_FIX.
"""

STEM = {
 47: 'If (x<sup>2</sup> + 1/x<sup>2</sup>) = 25 and x &gt; 0, then the value '
     'of (x<sup>7</sup> + 1/x<sup>7</sup>) is',
 48: 'For real values of x, the range of the function '
     'f(x) = (2x-3)/(2x<sup>2</sup>-4x-6) is',
 54: 'If f(x) = (x<sup>2</sup>+3x)(x<sup>2</sup>+3x+2), then the sum of all '
     'real roots of the equation √(f(x)+1) = 9701, is',
 68: 'The sum of all possible real values of x for which '
     'log<sub>x-3</sub>(x<sup>2</sup> - 9) = log<sub>x-3</sub>(x + 1) + 2, is',
}

OPTS = {
 24: ["Involving local people in cultivating forests.", "A ban on deforestation.",
      "Recognising the state’s claim to forest land use.",
      "Recognising the significance of forests to ecology."],
 47: ["44850√3", "44853√3", "44859√3", "44856√3"],
 48: ["(−∞, 1/8] ∪ [1, ∞)", "(−∞, 1/4] ∪ [1, ∞)", "(−∞, 1/4] ∪ [1/2, ∞)",
      "(−∞, 1/8] ∪ [1/2, ∞)"],
 54: ["-3", "3", "6", "-6"],
 68: ["-3", "√33", "(3 + √33)/2", "3"],
}

TAGS = {
 47: "Indices & Surds",       # unresolved: x²+1/x²=25, find x⁷+1/x⁷
 50: "Time & Work",           # unresolved: teams A,B,C job completion
 54: "Quadratic Equations",   # substitution y=x²+3x reduces to a quadratic
 59: "Alligation & Mixture",  # vessels A,B alcohol/water — mistagged as Ratio
 61: "Inequalities",          # p not less than 0.3q, not more than 0.7q — mistagged Quadrilaterals
 64: "Quadrilaterals",        # trapezium with inscribed circle — mistagged Circles
 65: "Triangles",             # unresolved: isosceles ΔABC, cevian AD extended to E
 67: "Simple Equations",      # school fees allocation — mistagged Time Speed Distance
}

# Q21-24's DIRECTION line uses "21 & 24" instead of "21-24"; see module docstring.
GROUP_RANGE_FIX = {(21, 21): (21, 24)}


def _fix_calls_ctx(body):
    lines = body.split('<br>')
    i = lines.index('Outgoing minutes to')
    rows = {
        'Anu': ('Xitel', '100', '—', '50', '225'),
        'Bijay': ('Xitel', '—', '200', '—', '125'),
        'Chetan': ('Yocel', '50', '175', '250', '150'),
        'Deepak': ('Yocel', '100', '150', '275', '100'),
        'Eshan': ('Yocel', '—', '100', '100', '375'),
        'Faruq': ('Yocel', '0', '—', '100', '150'),
    }
    table = ('<table><tr><th rowspan="2">Friend</th><th rowspan="2">Operator</th>'
             '<th colspan="2">Outgoing minutes to</th>'
             '<th colspan="2">Incoming minutes from</th></tr>'
             '<tr><th>Operator Xitel</th><th>Operator Yocel</th>'
             '<th>Operator Xitel</th><th>Operator Yocel</th></tr>')
    for name, vals in rows.items():
        table += '<tr><td>%s</td>%s</tr>' % (name, ''.join('<td>%s</td>' % v for v in vals))
    table += '</table>'
    tail_i = lines.index('It is known that the duration of calls from Faruq to '
                          'Eshan was 200 minutes. Also, there were no calls from:')
    return '<br>'.join(lines[:i]) + '<br>' + table + '<br>' + '<br>'.join(lines[tail_i:])


def _fix_buck_ctx(body):
    lines = body.split('<br>')
    i = lines.index('Round')
    rows = [
        ('Immediately to the left', 'Aarav'), ('Second to the right', '?'),
        ('Immediately to the right', 'Diya'), ('?', '?'), ('?', 'Aarav'),
        ('Second to the left', '?'), ('Immediately to the left', 'Gaurav'),
        ('Immediately to the left', '?'), ('?', 'Farhan'), ('?', 'Chirag'),
    ]
    table = '<table><tr><th>Round</th><th>Pass Type</th><th>Received by</th></tr>'
    for n, (pt, rb) in enumerate(rows, 1):
        table += '<tr><td>%d</td><td>%s</td><td>%s</td></tr>' % (n, pt, rb)
    table += '</table>'
    return '<br>'.join(lines[:i]) + '<br>' + table


CTX_FIX = {
 (25, 29): _fix_calls_ctx,
 (43, 46): _fix_buck_ctx,
}

# DILR is tagged one bucket per set (using the real ranges, not the raw
# misprinted group key — see module docstring point 2)
DILR_SETS = {
 (25, 28): "Tables & Data Sets",          # friend call-minutes table
 (29, 33): "Selection & Distribution",    # travelers/countries/spend
 (34, 37): "Sequencing & Scheduling",     # puzzle-competition progress charts
 (38, 42): "Conditional Logic & Puzzles", # trade-balance percentage deduction
 (43, 46): "Grid & Arrangements",         # circular seating, buck-passing
}

FIGS = {
 (34, 37): ('dilr-puzzle-progress.png',
            'Two step-line charts: total puzzles solved and visual puzzles '
            'solved over time (minutes) by four competitors — Anirbid, '
            'Chandranath, Koushik, Suranjan'),
}
