# -*- coding: utf-8 -*-
"""CAT 2025 Slot I — overrides.

Source defects:
1. Q40 ("Which two people tapped an equal number of times in total?") is
   printed as an open TITA answer box with no lettered options, but the
   answer key encodes it as a bare MCQ option number ("4", no TITA tag).
   The key file's own worked solution states the answer in words: "Alia and
   Badal tapped an equal number of times in total." Retyped as TITA with
   that text, same workaround as the CAT 2024 Slot 1 Q35 defect.
2. The DIRECTION line for the trade-tariff DILR set misprints "questions
   43-45" (should be "43-46"), so the extractor's context grouping left Q46
   without a shared context. GROUP_RANGE_FIX widens it.
"""

STEM = {
 49: 'In a circle with center C and radius 6√2 cm, PQ and SR are two '
     'parallel chords separated by one of the diameters. If ∠PQC = 45°, and '
     'the ratio of the perpendicular distance of PQ and SR from C is 3:2, '
     'then the area, in sq. cm, of the quadrilateral PQRS is',
}

OPTS = {
 46: ["Neither France nor UK", "Both France and UK", "Only France", "Only UK"],
 49: ["20(3 + √14)", "4(3 + √14)", "4(3√2 + √7)", "20(3√2 + √7)"],
 53: ["(4, √18) ∪ [5, √27) ∪ {6}", "(3, √10) ∪ [4, √17) ∪ {6}",
      "(3, √10) ∪ [5, √26) ∪ {6}", "[3, √10] ∪ [5, √26]"],
 59: ["10/3", "29/9", "13/4", "27/7"],
 63: ["–2", "–1/2", "2", "1/2"],
}

TAGS = {
 49: "Circles",                       # auto-tagger read garbled pre-fix stem
 53: "Functions",                     # greatest-integer / floor function
 54: "Percentages",                   # single-year weighted returns, not SI/CI
 56: "Permutations & Combinations",   # unresolved: sandwich order combinations
 58: "Quadratic Equations",           # x²-5x+k=0 integer-root count
 61: "Simple Equations",              # unresolved: stock share simultaneous eqns
 62: "Simple Equations",              # unresolved: a-6b+6c=4, 6a+3b-3c=50
 63: "Quadratic Equations",           # min/max of two quadratics
 64: "Percentages",                   # unresolved: boys/girls leaving class
}

# Q40 is printed as a TITA box with no options; see module docstring.
RETYPE = {40: ('tita', 'Alia and Badal')}

# Q43-46's DIRECTION line misprints "questions 43-45" — see module docstring.
GROUP_RANGE_FIX = {(43, 45): (43, 46)}

# DILR is tagged one bucket per set
DILR_SETS = {
 (25, 29): "Networks & Routes",         # train route A-E, segment seat occupancy
 (30, 34): "Sequencing & Scheduling",   # quarter-by-quarter Elite/Novice promotions
 (35, 38): "Grid & Arrangements",       # round table, 7 chairs, clockwise/ccw moves
 (39, 42): "Conditional Logic & Puzzles", # tapping-feet question game
 (43, 46): "Tables & Data Sets",        # import tariff radar + bar charts
}

FIGS = {
 (43, 45): ('dilr-tariff-radar.png',
            'Radar chart of the import tariff percentage charged by each of '
            'five countries — US, France, India, Japan, UK — on the others'),
}

# a second chart (the bar chart of tariffs in Billion USD) for the same set —
# FIGS only wires one image per group, so the rest are appended via CTX_FIX
_FIG2 = ('<div class="qfig"><img loading="lazy" src="img/pyq/2025/s1/dilr-tariff-bar.png" '
         'alt="Bar chart of the import tariff in Billion USD charged by each of five '
         'countries on the others"></div>')
CTX_FIX = {(43, 45): lambda body: body + _FIG2}
