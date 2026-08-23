# Paper ingestion — status & resume notes

Working state for the batch dropped in `papers to ingest/`. Update as papers land.

## Done (live on the site)

| Paper | Mock id | Questions | Notes |
|---|---|---|---|
| CAT 2023 Shift 1 | `cat2023shift1` | 66 | housing-grid figure |
| CAT 2023 Shift 2 | `cat2023shift2` | 66 | coin-boxes figure |
| CAT 2023 Shift 3 | `cat2023shift3` | 66 | street-network figure |
| CAT 2018 Slot 1 | `cat2018slot1` | 99 | LED-sales pie; see Q1 note below |

`mocks.json`: 15 mocks / 1084 questions. `tools/validate.py` and
`tools/smoke_test.js` both clean.

## Remaining

### CAT 2018 Slot 2 — ready to assemble (all analysis below is done)
`python tools/extract_pyq_paper.py "papers to ingest/CAT_2018_Slot_2_*.pdf" --out draft.json`
gives 100 questions / 100 keys, 34 VARC + 32 DILR + 34 QA, and **nothing needs
review except Q90's stem** (it is an image).

Group boundaries — `(first, last, ctx_paras)`, where `ctx_paras` counts the leading
paragraphs of the group leader's `head` that form the shared context:

- RC: `(1,5,5) (6,10,6) (11,15,3) (16,20,3) (21,24,5)`
- VARC standalone Q25–34: 25,26,27 Para-jumble · 28 Para-summary · 29 Odd One Out ·
  30 Para-summary · 31 Odd One Out · 32 Para-summary · 33 Odd One Out · 34 Para-jumble
- DILR: `(35,38,4)` Tables & Data Sets · `(39,42,2)` Conditional Logic & Puzzles ·
  `(43,46,7)` Tables & Data Sets · `(47,50,4)` Sequencing & Scheduling ·
  `(51,54,32)` Tables & Data Sets · `(55,58,7)` Tables & Data Sets ·
  `(59,62,2)` Venn Diagrams & Set Theory · `(63,66,2)` Venn Diagrams & Set Theory

Tables to rebuild as HTML (the text layer flattens them into loose rows) and the one
figure, all already verified against the rendered pages:

- Q43 leader paras[1..5] → brand table (Azra 40/15,000/10 · Bysi 25/20,000/30 ·
  Cxqi 15/30,000/40 · Dipq 20/25,000/30)
- Q47 leader paras[1..2] → venue log (7:10 "Akil, ?" · 7:15 ? · 7:25 ? · 7:30 Chitra ·
  7:40 Fatima · 7:45 ?)
- Q51 leader paras[6..17] → accreditation ranges; paras[19..27] → the eight-college
  grade table
- Q55 leader paras[2..4] → category table; the 23-box chart is already cropped to
  `img/pyq/2018/s2/dilr-product-boxes.png`

Q90's stem is an image; read off page 23:
`1/log₂100 − 1/log₄100 + 1/log₅100 − 1/log₁₀100 + 1/log₂₀100 − 1/log₂₅100 + 1/log₅₀100 = ?`
(options extract fine; key D → 1/2).

`secMin` is **60** for 2018/2019 papers (one hour per section), not 40.

### CAT 2019 Slot 1 — extracts cleanly, needs the same treatment
100 questions / 100 keys. Only these need vision (stems and/or options are images):
Q69, Q78, Q92, Q99, Q100. Already read:

- Q69 `If (5.55)ˣ = (0.555)ʸ = 1000, then the value of 1/x − 1/y is` — A) 2/3 B) 3 C) 1 D) 1/3, key D
- Q78 options — A) 1 : √3 · B) √3 : 2 · C) √2 : √3 · D) 2 : √5, key A
- Q92 `If a₁, a₂… are in A.P., then 1/(√a₁+√a₂) + … + 1/(√aₙ+√aₙ₊₁) is equal to` —
  A) (n−1)/(√a₁+√aₙ) · B) n/(√a₁−√aₙ₊₁) · C) (n−1)/(√a₁+√aₙ₋₁) · D) n/(√a₁+√aₙ₊₁), key D
- Q99 `If m and n are integers such that (√2)¹⁹ 3⁴ 4² 9ᵐ 8ⁿ = 3ⁿ 16ᵐ(⁴√64) then m is` —
  A) −16 B) −24 C) −20 D) −12, key D
- Q100 options — A) (1003)2¹⁵ − 3 · B) (997)2¹⁴ + 3 · C) (1003)¹⁵ + 6 · D) (997)¹⁵ − 3, key A

### CAT 2019 Slot 2 — BLOCKED, needs a different source file
This PDF is damaged and cannot be ingested faithfully as supplied:

- Question **text** exists only for Q2–Q25 (pages 3–25). Pages 26–65 carry the
  questions as **images with no text layer** — the content is visible when rendered
  but nothing is extractable.
- The **answer key only covers Q36–Q100** (65 keys). Q1–Q35 have no key at all.

The two sets do not overlap, so no question in this file has both its text and its
answer. Q36–100 could be recovered by transcribing ~40 rendered pages by hand, but
the VARC section (Q1–34) is unrecoverable either way. Best fix: re-download this
paper from the source.

## Known source defects (recorded, not worked around)

- **CAT 2018 Slot 1 Q1** — option C is absent from the PDF (page 2 ends at B), page 3
  opens at D)) while the key says C, and the explanation does not quote it. The
  question is **omitted** from `cat2018slot1`, which is why its VARC has 33 not 34.
- **CAT 2018 Slot 1 Q72** — the subscript 5 renders with an 's' glyph in this PDF's
  math font. Transcribed as log₅: option D, 1 + log₅(3/5) = log₅3, is exactly x,
  which agrees with the paper's key of D.

## Tooling added for this batch

- `tools/render_pdf.py` — PyMuPDF stand-in for pdftoppm/pdftotext/pdfinfo (no poppler
  on this machine).
- `tools/extract_response_sheet.py` — the CAT 2023 candidate-response-sheet format
  (per-question boxes, tick-coloured options, `Possible Answer:` for TITA).
- `tools/extract_pyq_paper.py` — the 2018/2019 "Previous Year Paper" format
  (`QNo:- N ,Correct Answer:- X` key block). Restores exponents/indices from span
  font size and baseline shift, slices options that share a line, and rebuilds
  paragraph breaks from vertical gaps.

Node is installed but not on PATH here — run the smoke test as
`"/c/Program Files/nodejs/node.exe" tools/smoke_test.js`.
