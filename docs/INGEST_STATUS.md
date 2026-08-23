# Paper ingestion — status & resume notes

Working state for the batch dropped in `papers to ingest/`. Update as papers land.

## Done (live on the site)

| Paper | Mock id | Questions | Notes |
|---|---|---|---|
| CAT 2023 Shift 1 | `cat2023shift1` | 66 | housing-grid figure |
| CAT 2023 Shift 2 | `cat2023shift2` | 66 | coin-boxes figure |
| CAT 2023 Shift 3 | `cat2023shift3` | 66 | street-network figure |
| CAT 2018 Slot 1 | `cat2018slot1` | 99 | LED-sales pie; see Q1 note below |
| CAT 2018 Slot 2 | `cat2018slot2` | 100 | 4 DILR tables + product-box chart |
| CAT 2019 Slot 1 | `cat2019slot1` | 100 | 3 DILR tables + street map, crime chart, vendor radar |

`mocks.json`: 17 mocks / 1284 questions. `tools/validate.py` and
`tools/smoke_test.js` both clean.

Every paper in the drop folder is now ingested except CAT 2019 Slot 2, below.

`secMin` is **60** for 2018/2019 papers (one hour per section), not 40.

> **If you re-extract an already-built paper, regenerate its draft first.** Drafts
> made before a tool fix are stale — a 2018 Slot 2 draft built that way had a
> trailing DIRECTIONS line and a mis-detected superscript inside some options.

## Remaining

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
