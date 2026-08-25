# Paper ingestion — status & resume notes

Working state for the papers in `papers/` and `papers to ingest/`. Update as papers land.

## Done (live on the site)

| Paper | Mock id | Questions |
|---|---|---|
| CAT 2017 Slot I / II | (pre-existing) | — |
| CAT 2020 Slot I / II / III | (pre-existing) | — |
| CAT 2021 Slot 1 / 2 / 3 | (pre-existing) | — |
| CAT 2022 Slot 1 / 2 / 3 | (pre-existing) | — |
| CAT 2023 Shift 1 / 2 / 3 | `cat2023shift1-3` | 66 each |
| CAT 2018 Slot 1 | `cat2018slot1` | 99 (see Q1 note) |
| CAT 2018 Slot 2 | `cat2018slot2` | 100 |
| CAT 2019 Slot 1 | `cat2019slot1` | 100 |
| CAT 2019 Slot 2 | `cat2019slot2` | 100 |
| CAT 2024 Slot 1 | `cat2024slot1` | 68 |
| CAT 2024 Slot 2 | `cat2024slot2` | 68 |
| CAT 2024 Slot 3 | `cat2024slot3` | 68 |
| CAT 2025 Slot 1 | `cat2025slot1` | 68 |
| CAT 2025 Slot 2 | `cat2025slot2` | 68 |

`mocks.json`: **23 mocks / 1724 questions**. `tools/validate.py` and the smoke test
both clean.

## Remaining: CAT 2025 Slot 3

Already extracted cleanly — **68 questions and 68 keys, correct 24/22/22 section
split**. Draft regenerates in seconds:

```
python tools/extract_split_paper.py "papers/Actual-CAT-2024-Slot-II.pdf" \
       "papers/Actual-CAT-2024-Slot-II-(Answer-Keys).pdf" --out draft.json
```

Per paper, three things remain. The scratch build harness
(`build_split.py` + `ov_<tag>.py`) mirrors what `cat2024slot1`/`2`/`3` used.
`build_split.py` also supports a per-group `GROUP_RANGE_FIX` override (widens
which question numbers pick up a shared context/figure, independent of the
FIGS/CTX_FIX lookup key) — needed once already, see the 2024 Slot 3 defect below.

**1. Topic tags** — `python tools/suggest_topics.py draft.json` proposes all of them,
but it runs against the *raw* (pre-override) extracted text, so a stem the extractor
mangled can throw the keyword match off even when unresolved count is 0 — cross-check
tags for every flagged question, not just the literal unresolved list. Unresolved after
the auto-pass: 2025s3 `[47,50,65]`. DILR must additionally be named one bucket per SET
(INGEST_NOTES.md) — the keyword pass spreads them across a set otherwise.

**2. Figures** — `python tools/find_figures.py <paper> --pages N --save <path>` crops
from the PDF's own geometry, no coordinate guessing. For a diagram built from vector
lines + text labels (not a raster chart) the auto-detected cluster can be too tight
(only the rules, not the labels) — pass `--pad 60` or so, then trim the padded PNG with
PIL to the true diagram bounds. A DILR set can carry two charts on two different pages
(2025s1's tariff radar + bar) or two charts stacked on one page that
`find_figures.py` merges into a single cluster (2025s2's research-paper bar charts,
cropped as one tall image) — `FIGS` only wires one image per group key, so append a
second image via `CTX_FIX = {key: lambda body: body + FIG2_HTML}` (CTX_FIX runs after
FIGS, so it receives the body with the first image already appended). Pages with
charts: 2025s3 `10,12,13,14`.

**3. Questions whose maths is vector-drawn** (radical overlines and fraction bars have
no text-layer presence, so they vanish). Audit that finds them precisely:
`scratchpad/ingest/new/audit.py`. Lists:
2025s3 `[47,48,54,68]`.

### CAT 2025 Slot 2 defects worked around (for reference — this paper is done)
- **TITA question keyed as MCQ**: Q63 ("number of divisors ... of the form 3r+1") is
  printed as an open TITA answer box with no lettered options, but the key gives it a
  bare option number ("4", no TITA tag) — third occurrence of this exact pattern (see
  2025 Slot 1 Q40, 2024 Slot 1 Q35). The key's own worked solution ends "Final Answer =
  42", so it's stored as TITA with that number.

### CAT 2025 Slot 1 defects worked around (for reference — this paper is done)
- **TITA question keyed as MCQ**: Q40 ("Which two people tapped an equal number of
  times in total?") is printed as an open TITA answer box with no lettered options, but
  the key file gives it a bare option number ("4", no TITA tag) — the same pattern as
  the CAT 2024 Slot 1 Q35 defect. The key file's own worked solution states the answer
  in words ("Alia and Badal tapped an equal number of times in total"), so it's stored
  as TITA with that exact text — the site's grading does a case-insensitive string
  match, so a name-pair answer works the same way a numeric one would.
- **Misprinted DIRECTION range**: the tariff DILR set's direction line says "questions
  43-45" (should be "43-46"), leaving Q46 without a shared context — same fix pattern as
  2024 Slot 3's GDP table, `GROUP_RANGE_FIX = {(43, 45): (43, 46)}`.

### CAT 2024 Slot 3 defects worked around (for reference — this paper is done)
- **Misprinted DIRECTION range**: the source's own direction line for the GDP-table DILR
  set reads "for the question 37 to 37" (should say "34 to 37"), so the extractor's
  context grouping only attached Q37 to the passage and left Q34-36 without a shared
  context. Fixed with `GROUP_RANGE_FIX = {(37, 37): (34, 37)}` in `ov_2024s3.py` — the
  four questions already extracted correctly on their own, only the context link needed
  widening.
- **Table with dropped numeric cells**: the foodgrain-nutrient DILR table (Q43-46) has
  its header/label text extracted fine but every numeric data cell vanished from the
  text layer. Rebuilt by hand from the rendered page image (`CTX_FIX` in `ov_2024s3.py`),
  blanks shown as "—" to match the source's own "table has some missing values" framing.

## Known source defects (recorded, not worked around)

- **CAT 2018 Slot 1 Q1** — option C is absent from the PDF while the key says C, and the
  explanation does not quote it. The question is **omitted**, hence 99 not 100.
- **CAT 2018 Slot 1 Q72** — subscript 5 renders with an 's' glyph. Transcribed as log₅;
  option D, 1 + log₅(3/5) = log₅3, is exactly x, agreeing with the key.
- **CAT 2024 Slot 1 Q35** — printed as a type-in box with no options, but the key file
  gives the letter D (impossible for a TITA). That D is Q34's answer duplicated. The
  same file's worked solution says "value of SPV of 4 shares i.e A, C, D and G is
  greater than 0.5", so it is stored as TITA with answer 4.
- **CAT 2019 Slot 2 (old copy in `papers to ingest/`)** — had question text only for
  Q2-25 and keys only for Q36-100, so no question had both. Superseded by
  `papers/Actual-CAT-2019-Slot-II.pdf`, which is complete. The old file can be ignored.

## Tooling

Three extractors, one per source format:
- `tools/extract_response_sheet.py` — CAT 2023 candidate response sheets (per-question
  boxes, tick-coloured options, `Possible Answer:` for TITA).
- `tools/extract_pyq_paper.py` — 2018/2019 Testbook "Previous Year Paper"
  (`QNo:- N ,Correct Answer:- X` key block). Restores exponents/indices from span font
  size and baseline shift, and Adobe Symbol maths glyphs.
- `tools/extract_split_paper.py` — 2024/2025 where paper and key are separate files.
  Handles both key dialects (letters vs option numbers with `(TITA)` tags).

Support: `tools/render_pdf.py` (poppler-free rendering), `tools/find_figures.py`
(crop figures from PDF geometry), `tools/suggest_topics.py` (propose topic tags).

Node is installed but NOT on PATH — run the smoke test as
`"/c/Program Files/nodejs/node.exe" tools/smoke_test.js`.
`secMin` is 40 for 2021-2025 papers and 60 for 2018/2019.
