# -*- coding: utf-8 -*-
"""CAT 2024 Slot I — stems/options whose maths is drawn rather than typed (radical
overlines and fraction bars are vector rules with no text-layer presence). Read off
the rendered pages 12, 16 and 17. Values are HTML-ready."""

STEM = {
 35: "Daily Share Price Variability (SPV) is defined as (Day’s high price − Day’s low "
     "price) / (Average of the opening and closing prices during the day). How many "
     "shares had an SPV greater than 0.5 on that day?",
 62: "If (a + b√n) is the positive square root of (29 − 12√5), where a and b are "
     "integers, and n is a natural number, then the maximum possible value of "
     "(a + b + n) is",
 65: "The sum of all real values of k for which (1/8)<sup>k</sup> × "
     "(1/32768)<sup>1/3</sup> = 1/8 × (1/32768)<sup>1/k</sup>, is",
 68: "For any natural number n, let a<sub>n</sub> be the largest integer not exceeding "
     "√n. Then the value of a<sub>1</sub> + a<sub>2</sub> + ….+ a<sub>50</sub> is",
}

OPTS = {
 55: ["1 1/3", "3", "1", "4"],
 59: ["1125π√2", "750π√2", "1125π", "750π"],
 65: ["−4/3", "−2/3", "4/3", "2/3"],
}

# Q35 is printed with a type-in answer box (no options), but the key file gives it the
# letter D — impossible for a TITA. That D is Q34's answer duplicated: Q34 asks which
# share had the HIGHEST SPV and D does (1.2). The same file's worked solution for Q35
# ends "value of SPV of 4 shares i.e A, C, D and G is greater than 0.5", so the count
# is 4. Retype the question as TITA with that answer rather than trust the letter.
RETYPE = {35: ('tita', '4')}

# DILR is tagged one bucket per set
DILR_SETS = {
 (25, 29): "Games & Tournaments",            # the game of QUIET, six teams
 (30, 33): "Venn Diagrams & Set Theory",     # countries visited by three people
 (34, 37): "Tables & Data Sets",             # candlestick share-price chart
 (38, 41): "Tables & Data Sets",             # stars received by two bloggers
 (42, 46): "Conditional Logic & Puzzles",    # Amiya vs Ramya campaign outcomes
}

FIGS = {
 (30, 33): ('dilr-countries-visited.png',
            'Bar chart of the number of countries visited by Dheeraj, Samantha and '
            'Nitesh, split into Asia, Europe and the rest of the world'),
 (34, 37): ('dilr-share-prices.png',
            'Candlestick chart of day high, open, close and low prices for seven '
            'shares A to G, bullish shares in green and bearish in red, with a legend'),
 (38, 41): ('dilr-web-surfers.png',
            'Bar chart of the number of stars received by bloggers A and B from each '
            'of the surfers M, N, O, P, X and Y'),
}
