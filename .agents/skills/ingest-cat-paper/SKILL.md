---
name: ingest-cat-paper
description: Turn a CAT question-paper PDF into verified mock tests in mocks.json, with figures and topic tags. Use whenever the user gives a CAT paper PDF and asks to ingest / add / inject it into the app.
---

# Ingest a CAT paper

Goal: append one mock object per slot to `mocks.json`, save figures under
`img/pyq/<year>/<slot>/`, with **every answer verified against the source PDF**.

Full spec: **`docs/INGEST_FRAMEWORK.md`** (read it before starting). This skill is the
short operating loop; the framework has the schema, taxonomy and detail.

## Steps

1. **Render + extract**
   ```bash
   pdfinfo "paper.pdf"                                    # page count
   pdftoppm -png -r 150 -f A -l B "paper.pdf" pg_         # page images
   pdftotext -layout -f A -l B "paper.pdf" paper.txt      # text for stems/passages/options
   ```

2. **Map structure** — find the VARC / DILR / QA section boundaries, the questions, their
   types (MCQ vs TITA), and which questions share a passage or DILR-set context.

3. **Answers**
   - Solved (green-tick) PDF: `python3 tools/detect.py pg_042.png` for MCQ; `Possible Answer:`
     text for TITA. **Vision-check any page that isn't 4-marks/1-green.**
   - Unsolved PDF: parse the answer-key block (`QNo:- N , Correct Answer:- X`); MCQ letter→index.

4. **Figures / tables / math**
   - `python3 tools/crop_figure.py pg_069.png img/pyq/2023/s1/name.png --box 0.10 0.06 0.68 0.29`
   - Rebuild tables as real HTML `<table>`. Transcribe math to Unicode (`√ × − ≤`, `<sup>/<sub>`).

5. **Tag topics** — give every question a `sub` (VARC by type, DILR per set, QA fine subtopic).
   See framework §6 and `INGEST_NOTES.md`.

6. **Assemble** — build the mock (schema in framework §1), append to `mocks.json`
   (`ensure_ascii=False`, keep existing entries). VARC passages fill `ctxs` first, then DILR
   contexts; question `c` indexes into that flat array.

7. **Validate + commit**
   ```bash
   python3 tools/validate.py        # must say OK
   node tools/smoke_test.js         # must say REAL ERRORS: 0   (npm i jsdom first)
   git add -A && git commit -m "CAT <year> Slot <n> full mock (…)"
   ```

## Guardrails
Never invent data. Correctness > speed. "Chosen Option" ≠ answer key. Append, don't rewrite.
Only edit `mocks.json` + add `img/` files.
