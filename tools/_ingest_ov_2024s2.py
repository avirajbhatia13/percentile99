# -*- coding: utf-8 -*-
"""CAT 2024 Slot II — overrides for questions whose text/options the extractor
mangled (a para-summary whose options ran onto the next page; maths drawn as
vector rules with no text-layer presence). Values are HTML-ready."""

STEM = {
 3: 'Different from individuals, states conduct warfare operations using the DIME '
    'model — "diplomacy, information, military, and economics." Most states do '
    'everything they can to inflict pain and confusion on their enemies before '
    'deploying the military. In fact, attacks on vectors of information are a '
    'well-worn tactic of war and usually are the first target when the charge '
    "begins. It's common for telecom data and communications networks to be "
    'routinely monitored by governments, which is why the open data policies of '
    'the web are so concerning to many advocates of privacy and human rights. '
    'With the worldwide adoption of social media, more governments are getting '
    'involved in low-grade information warfare through the use of cyber troops. '
    'According to a study by the Oxford Internet Institute in 2020, cyber troops '
    'are "government or political party actors tasked with manipulating public '
    'opinion online." The Oxford research group was able to identify 81 '
    'countries with active cyber troop operations utilizing many different '
    'strategies to spread false information, including spending millions on '
    'online advertising.',
 51: "If (x + 6√2)<sup>1/2</sup> − (x − 6√2)<sup>1/2</sup> = "
     "2√2, then x equals",
 56: 'The sum of the infinite series (1/5)(1/5 − 1/7) + (1/5)<sup>2</sup>'
     '((1/5)<sup>2</sup> − (1/7)<sup>2</sup>) + (1/5)<sup>3</sup>'
     '((1/5)<sup>3</sup> − (1/7)<sup>3</sup>) + … equals',
 61: 'The roots α, β of the equation 3x<sup>2</sup> + λx − 1 = 0, '
     'satisfy 1/α<sup>2</sup> + 1/β<sup>2</sup> = 15. The value of '
     '(α<sup>3</sup> + β<sup>3</sup>)<sup>2</sup>, is',
 62: 'All the values of x satisfying the inequality 1/(x+5) ≤ 1/(2x−3) '
     'are',
 66: 'If a, b and c are positive real numbers such that a &gt; 10 ≥ b ≥ '
     'c and log<sub>8</sub>(a+b)/log<sub>2</sub>c + log<sub>27</sub>(a−b)/'
     'log<sub>3</sub>c = 2/3, then the greatest possible integer value of a is',
}

OPTS = {
 3: ["Governments primarily use the DIME model to deploy cyber troops who "
     "practise low-grade information warfare, seeking to manipulate public "
     "opinion with the objective of inflicting pain and confusion on their "
     "enemies.",
     "Following the DIME model, many governments have taken advantage of open "
     "data policies of the web to deploy cyber troops who manipulate domestic "
     "public opinion, using advertising and other strategies to spread false "
     "information.",
     "Using the DIME model, together with military operations, many "
     "governments simultaneously conduct information warfare with the help of "
     "cyber troops and routinely monitor telecom data and communications "
     "networks.",
     "As part of conducting information warfare as per the DIME model, many "
     "governments routinely monitor telecom data and communications networks, "
     "and use cyber troops on social media to manipulate public opinion."],
 50: ["4 : 5", "3 : 5", "5 : 3", "5 : 4"],
 56: ["5/408", "7/816", "7/408", "5/816"],
 59: ["4 + 2√3 : 1", "7 + 4√3 : 1", "2 + √3 : 1", "4 + √3 : 1"],
 61: ["16", "4", "1", "9"],
 62: ["−5 &lt; x &lt; 3/2 or 3/2 &lt; x ≤ 8",
      "−5 &lt; x &lt; 3/2 or x &gt; 3/2",
      "x &lt; −5 or x &gt; 3/2",
      "x &lt; −5 or 3/2 &lt; x ≤ 8"],
}

TAGS = {51: "Indices & Surds"}   # √(x+6√2) − √(x−6√2) = 2√2 — surd equation

# DILR is tagged one bucket per set
DILR_SETS = {
 (25, 29): "Grid & Arrangements",         # 1-10 placed in a 4x4 grid, row/col rules
 (30, 33): "Networks & Routes",           # walkways/lakes schematic, distances
 (34, 37): "Tables & Data Sets",          # daily/cumulative rating averages + bar chart
 (38, 41): "Tables & Data Sets",          # firm PAT/ES/PRD bubble scatter plots
 (42, 46): "Selection & Distribution",    # 8 players distributed among 3 coaches
}

FIGS = {
 (34, 37): ('dilr-ratings-distribution.png',
            'Bar chart titled Distribution of Ratings on Day 2, showing the '
            'number of buyers who gave each rating from 1 to 5'),
 (38, 41): ('dilr-firms-pat-es.png',
            'Two bubble scatter plots for 2019 and 2023 plotting six firms A to '
            'F by employee strength (ES) on the x-axis and profit after tax '
            '(PAT) on the y-axis, with bubble area proportional to R&D spend '
            '(PRD)'),
}
