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

`mocks.json`: **20 mocks / 1520 questions**. `tools/validate.py` and the smoke test
both clean.

## Remaining: CAT 2024 Slot 3, CAT 2025 Slots 1-3

All four are already extracted cleanly — **68 questions and 68 keys each, correct
24/22/22 section split**. Drafts regenerate in seconds:

```
python tools/extract_split_paper.py "papers/Actual-CAT-2024-Slot-II.pdf" \
       "papers/Actual-CAT-2024-Slot-II-(Answer-Keys).pdf" --out draft.json
```

Per paper, three things remain. The scratch build harness
(`build_split.py` + `ov_<tag>.py`) mirrors what `cat2024slot1`/`cat2024slot2` used.

**1. Topic tags** — `python tools/suggest_topics.py draft.json` proposes all of them.
Unresolved after that: 2024s3 `[57]`, 2025s1 `[56,61,62,64]`,
2025s2 `[60,62]`, 2025s3 `[47,50,65]`. DILR must additionally be named one bucket
per SET (INGEST_NOTES.md) — the keyword pass spreads them across a set otherwise.

**2. Figures** — `python tools/find_figures.py <paper> --pages N --save <path>` crops
from the PDF's own geometry, no coordinate guessing. Pages with charts:
2024s3 `12,13,14,15`; 2025s1 `12,13,15,16`; 2025s2 `13,14,15`;
2025s3 `10,12,13,14`.

**3. Questions whose maths is vector-drawn** (radical overlines and fraction bars have
no text-layer presence, so they vanish). Audit that finds them precisely:
`scratchpad/ingest/new/audit.py`. Lists:
2024s3 `[28,49,55,56,58,60,61,63,66,67]`,
2025s1 `[40,49,53,59,63]`, 2025s2 `[45,47,48,49,54,63]`, 2025s3 `[47,48,54,68]`.

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
