# -*- coding: utf-8 -*-
"""CAT 2024 Slot III — overrides. Maths whose radicals/fraction bars are vector
rules with no text-layer presence (read off the rendered pages 15-18), plus two
source defects:

1. The DIRECTION line for Q34-37 misprints "for the question 37 to 37" (should
   be "34 to 37"), so the extractor's context-range grouping only captured Q37
   under that context and left Q34-36 context-less. GROUP_RANGE_FIX widens the
   (37, 37) group's question range to (34, 37) when assigning ctx_of, without
   touching the FIGS/CTX_FIX lookup key (which stays the raw (37, 37)).
2. The foodgrain table (Q43-46) has values positioned so the text layer drops
   every numeric cell — only the header/label text survives. Rebuilt by hand
   from the rendered page image, blanks shown as '—' to match the source's own
   'table has some missing values' framing.
"""

STEM = {
 28: 'What best can be said about the road distance (in km) between the ATMs '
     'having the second highest and the second lowest cash requirements?',
 49: 'A circular plot of land is divided into two regions by a chord of '
     'length 10√3 meters such that the chord subtends an angle of 120° at '
     'the center. Then, the area, in square meters, of the smaller region is',
 56: 'If (a + b√3)<sup>2</sup> = 52 + 30√3, where a and b are natural numbers, '
     'then a + b equals',
 58: 'The sum of all distinct real values of x that satisfy the equation '
     '10<sup>x</sup> + 4/10<sup>x</sup> = 91/2, is',
 60: 'A certain amount of water was poured into a 300 litre container and the '
     'remaining portion of the container was filled with milk. Then an amount '
     'of this solution was taken out from the container which was twice the '
     'volume of water that was earlier poured into it, and water was poured '
     'to refill the container again. If the resulting solution contains 72% '
     'milk, then the amount of water, in litres, that was initially poured '
     'into the container was',
 61: 'For any non–zero real number x, let f(x) + 2f(1/x) = 3x. Then, the sum '
     'of all possible values of x for which f(x) = 3, is',
 63: 'Consider the sequence t<sub>1</sub> = 1, t<sub>2</sub> = −1 and '
     't<sub>n</sub> = ((n−3)/(n−1)) t<sub>n−2</sub> for n ≥ 3. Then, the value '
     'of the sum 1/t<sub>2</sub> + 1/t<sub>4</sub> + 1/t<sub>6</sub> + …… + '
     '1/t<sub>2022</sub> + 1/t<sub>2024</sub>, is',
 66: 'Sam can complete a job in 20 days when working alone. Mohit is twice '
     'as fast as Sam and thrice as fast as Ayna is the same job. The '
     'undertake a job with an arrangement where Sam and Mohit work together '
     'on the first day, Sam and Ayna on the second day, Mohit and Ayna on '
     'the third day, and this three–day pattern is repeated till the work '
     'gets completed. Then, the fraction of total work done by Sam is',
 67: 'A regular octagon ABCDEFGH has sides on length 6 cm each. Then the '
     'area, in sq. cm, of the square ACEG is',
}

OPTS = {
 28: ["4 km", "5 km", "Either 4 km or 7 km", "7 km"],
 49: ["20(4π/3 + √3)", "20(4π/3 − √3)", "25(4π/3 − √3)", "25(4π/3 + √3)"],
 55: ["75 and 96, respectively", "75 and 90, respectively",
      "72 and 88, respectively", "72 and 80, respectively"],
 56: ["8", "10", "7", "9"],
 61: ["–2", "3", "2", "–3"],
 66: ["3/20", "3/10", "1/5", "1/20"],
 67: ["36(2 + √2)", "72(1 + √2)", "36(1 + √2)", "72(2 + √2)"],
}

TAGS = {
 56: "Indices & Surds",      # (a+b√3)² = 52+30√3 — auto-tagger read it off garbled text
 57: "Triangles",            # unresolved: midpoints/medians of ABC, area of XYZ
 58: "Logarithms",           # 10^x + 4/10^x = 91/2 — solved via log, not a series
 60: "Alligation & Mixture", # water/milk container — mistagged from Q61's leaked text
 66: "Time & Work",          # Sam/Mohit/Ayna work rates — mistagged from "arrangement"
 67: "Mensuration",          # regular octagon area — no dedicated polygon bucket
}

# Q34-37's DIRECTION line misprints "for the question 37 to 37" — see module
# docstring. The group's raw key stays (37, 37) for FIGS/CTX_FIX lookup below.
GROUP_RANGE_FIX = {(37, 37): (34, 37)}


def _fix_gdp_ctx(body):
    lines = body.split('<br>')
    i = lines.index('Country')
    header, rows, j = lines[i:i + 5], [], i + 5
    for _ in range(8):
        rows.append(lines[j:j + 5]); j += 5
    table = '<table><tr>' + ''.join('<th>%s</th>' % h for h in header) + '</tr>'
    for r in rows:
        table += '<tr>' + ''.join('<td>%s</td>' % c for c in r) + '</tr>'
    table += '</table>'
    tail_i = lines.index('Assume that the GDP growth rates and population '
                          'growth rates of the countries will remain constant for the')
    tail = ' '.join(lines[tail_i:tail_i + 2])
    return '<br>'.join(lines[:i]) + '<br>' + table + '<br>' + tail


def _fix_foodgrain_ctx(body):
    lines = body.split('<br>')
    i = lines.index('Food grain')
    data = {
        'C1': (None, None, '0', '12'), 'C2': (None, None, '3', '10'),
        'M1': ('62', '10', None, None), 'M2': (None, None, '7', '16'),
        'M3': ('56', None, '12', None), 'P1': ('66', None, None, '10'),
        'P2': (None, '14', None, '8'),
    }
    def row(vals): return ''.join('<td>%s</td>' % (v or '—') for v in vals)
    table = ('<table><tr><th>Food grain category</th><th>Codename</th>'
              '<th>Carbohydrate</th><th>Protein</th><th>Fat</th>'
              '<th>Other nutrients</th></tr>'
              '<tr><td rowspan="2">Cereal</td><td>C1</td>%s</tr>'
              '<tr><td>C2</td>%s</tr>'
              '<tr><td rowspan="3">Millet</td><td>M1</td>%s</tr>'
              '<tr><td>M2</td>%s</tr>'
              '<tr><td>M3</td>%s</tr>'
              '<tr><td rowspan="2">Pseudo-cereal</td><td>P1</td>%s</tr>'
              '<tr><td>P2</td>%s</tr></table>'
              % (row(data['C1']), row(data['C2']), row(data['M1']),
                 row(data['M2']), row(data['M3']), row(data['P1']), row(data['P2'])))
    tail_i = lines.index('The following additional facts are known.')
    return '<br>'.join(lines[:i]) + '<br>' + table + '<br>' + '<br>'.join(lines[tail_i:])


CTX_FIX = {
 (37, 37): _fix_gdp_ctx,
 (43, 46): _fix_foodgrain_ctx,
}

# DILR is tagged one bucket per set
DILR_SETS = {
 (25, 29): "Networks & Routes",         # road-network diagram, ATM cash requirements
 (30, 33): "Tables & Data Sets",        # OTT Kid/Elder subscriber percentages + bar chart
 (34, 37): "Tables & Data Sets",        # GDP / GDP-per-capita table for 8 countries
 (38, 42): "Sequencing & Scheduling",   # AC on/off timeline + inside-temperature chart
 (43, 46): "Tables & Data Sets",        # foodgrain nutrient table with missing values
}

FIGS = {
 (25, 29): ('dilr-atm-network.png',
            'Grid diagram of three horizontal roads R-A, R-B, R-C crossed by '
            'three vertical roads V1, V2, V3, with the distance between '
            'adjacent intersections marked and the total ATM cash requirement '
            'at the end of each road'),
 (30, 33): ('dilr-ott-subscribers.png',
            "Bar chart of the percentage of total OTT subscribers in the "
            "'Kid' and 'Elder' categories for 2023 and 2024"),
 (38, 42): ('dilr-ac-temperature.png',
            'Line chart of the inside temperature of a room in degrees '
            'Celsius from 11 pm to 2 am, showing a repeated rise and fall '
            'pattern as the AC is switched between modes'),
}
