# -*- coding: utf-8 -*-
"""CAT 2025 Slot II — overrides.

Source defect: Q63 ("number of divisors ... of the form 3r+1") is printed as
an open TITA answer box with no lettered options, but the key gives it a bare
MCQ option number ("4", no TITA tag) — the same pattern as CAT 2025 Slot 1
Q40 and CAT 2024 Slot 1 Q35. The key file's own worked solution ends "Final
Answer = 42", so it's stored as TITA with that number rather than the
mis-keyed option letter.
"""

STEM = {
 45: 'Which of the following statements about the relative sizes of the '
     'hoops is true?',
 49: 'If log<sub>64</sub>x<sup>2</sup> + log<sub>8</sub>√y + '
     '3log<sub>512</sub>(√y z) = 4, where x, y and z are positive real '
     'numbers, then the minimum possible value of (x + y + x) is',
 54: 'Let f(x) = x/(2x-1) and g(x) = x/(x-1). Then, the domain of the '
     'function h(x) = f(g(x)) + g(f(x)) is all real numbers except',
}

OPTS = {
 45: ["H2 < H4 < H3 < H1", "H2 < H3 < H4 < H1", "H1 < H3 < H4 < H2",
      "H1 < H4 < H3 < H2"],
 47: ["8/3 + p + 1/3 q", "2/3 − 2p + 2/3 q", "8/3 − p + 3/2 q",
      "2/3 − p + 3/2 q"],
 48: ["6 : 19", "5 : 24", "7 : 24", "6 : 25"],
 49: ["96", "36", "24", "48"],
 54: ["1/2, 1, and 3/2", "−1/2, 1/2, and 1", "−1, 1/2 and 1", "1/2, and 1"],
}

TAGS = {
 47: "Quadratic Equations",   # common-root sum-of-roots — auto-tagged from garbled stem
 48: "Mensuration",           # hexagon/trapezium area ratio — no polygon-specific bucket
 50: "Inequalities",          # (x²-|x+9|+x)>0
 53: "Geometric Progression", # decreasing infinite GP, a1+a2+a3=52
 54: "Functions",             # h(x)=f(g(x))+g(f(x)) domain — auto-tagged from garbled stem
 58: "Quadratic Equations",   # x²-5x+k=0, integer-root count
 59: "Averages",              # book sales averages across days
 60: "Indices & Surds",       # unresolved: 9^(...) - 4(3^...) + 27 = 0
 62: "Triangles",             # unresolved: cevians BE, AD in ΔABC, BD:CD
 63: "Factors",               # divisors of the form 3r+1
 64: "TSD – Boats & Streams", # Rita/Sneha rowing upstream/downstream
}

# Q63 is printed as a TITA box with no options; see module docstring.
RETYPE = {63: ('tita', '42')}

# DILR is tagged one bucket per set
DILR_SETS = {
 (25, 29): "Sequencing & Scheduling",   # musicians trained under gurus, year spans
 (30, 33): "Tables & Data Sets",        # Sustainability Index scatter plot
 (34, 38): "Conditional Logic & Puzzles", # pollution-measure deduction, no chart
 (39, 42): "Tables & Data Sets",        # two research-paper bar charts
 (43, 46): "Conditional Logic & Puzzles", # ball/hoop ping deduction
}

FIGS = {
 (30, 33): ('dilr-si-scatter.png',
            'Scatter plot of six countries A to F, with x-axis the percentage '
            'increase in Sustainability Index in 2020 from 2016 and y-axis '
            'the percentage increase in 2024 from 2020'),
 (39, 42): ('dilr-research-papers.png',
            'Two bar charts: the number of research papers written by each '
            'of four authors — Arman, Brajen, Chintan, Devon — and the '
            'number of papers by type — single-author, two-author, '
            'three-author, four-author'),
}
