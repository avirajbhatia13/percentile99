# CAT paper ingestion framework

This is a complete, self-contained spec for turning a CAT question-paper PDF into
mock tests inside `mocks.json`, with verified answers, figures and topic tags. Any
capable coding agent (Google Antigravity / Gemini, Cursor, Claude Code) can follow it
end-to-end. It was reverse-engineered from the pipeline that produced the CAT
2017 / 2020 / 2021 / 2022 mocks already in this repo — copy their structure when in doubt.

> **Golden rule:** never invent an answer, a figure, or a question. Every value must come
> from the source PDF. When the automated tools are ambiguous, fall back to *reading the
> rendered page image* (vision) and transcribing what is actually printed. Correctness beats
> speed — a wrong answer key is worse than a missing paper.

---

## 0. What you produce

For each paper you add **one mock object per slot/shift** to the array in `mocks.json`,
and you save any figures as PNGs under `img/pyq/<year>/<slotFolder>/`.

A CAT paper = 3 sections in fixed order: **VARC** (Verbal Ability & Reading Comprehension),
**DILR** (Data Interpretation & Logical Reasoning), **QA** (Quantitative Ability).

---

## 1. Data schema (exact)

`mocks.json` is a single JSON array of mock objects. Append; never rewrite existing entries.

```jsonc
{
  "id": "cat2023slot1",        // lowercase, unique: cat<year>slot<n>
  "name": "CAT 2023 Slot 1",   // display name
  "year": 2023,                // integer
  "secMin": 40,                // minutes PER SECTION (CAT = 40)
  "ctxs": [ "<p>passage html…</p>", "…" ],   // shared passage / DILR-set contexts
  "sections": [
    { "name": "VARC", "qs": [ /* question objects */ ] },
    { "name": "DILR", "qs": [ … ] },
    { "name": "QA",   "qs": [ … ] }
  ]
}
```

**Question object:**

```jsonc
{
  "n": 1,                 // 1-based index WITHIN its section
  "c": 0,                 // index into this mock's ctxs[], or null if standalone
  "type": "mcq",          // "mcq" | "tita"
  "q": "Question stem as HTML…",
  "opts": ["A","B","C","D"],   // 4 strings for mcq; [] for tita
  "ans": 2,               // mcq: 0-based index of correct option; tita: the answer as a STRING
  "sol": "",              // optional worked solution (may be empty)
  "sub": "Percentages"    // REQUIRED topic tag — see §6
}
```

Hard rules the validator enforces (`tools/validate.py`):
- `type` is `"mcq"` or `"tita"`.
- mcq → `opts.length === 4`, all non-empty, `ans` is int in `0..3`.
- tita → `ans` is a string.
- `c` is `null` or a valid index into `ctxs`.
- `sub` is a non-empty string.

### How `ctxs` indexing works
`ctxs` is a **flat, mock-global array**. Build it as *VARC passages first, then DILR set
contexts*. VARC RC questions point at their passage's index (0,1,2,3…); DILR questions point
at their set context's index (which continues after the VARC passages). QA questions are
almost always standalone → `c: null`. Example: 4 VARC passages = ctx 0–3, 4 DILR sets = ctx
4–7; a DILR question in the 2nd set has `c: 5`.

The app resolves a drill question's context via `MOCKS[_m].ctxs[q.c]`, so the indices must be
correct or passages/tables won't show.

---

## 2. Environment / tools you need

- `pdftoppm`, `pdftotext`, `pdfinfo` (poppler-utils) — render & extract PDFs.
- Python 3 with **Pillow** (`pip install pillow --break-system-packages`) — figure crop + tick detector.
- Node.js with **jsdom** (`npm i jsdom`) — headless load test.
- The repo's `tools/detect.py`, `tools/validate.py`, `tools/smoke_test.js`.

Render at 150 DPI (good balance of legibility vs size):
```bash
pdftoppm -png -r 150 -f <first> -l <last> "paper.pdf" pages_
pdftotext -layout -f <first> -l <last> "paper.pdf" paper.txt
```

**No poppler installed (e.g. this Windows box)?** Use the PyMuPDF-based stand-in instead
— same page-numbering convention, everything else below reads unchanged:
```bash
pip install -r tools/requirements.txt      # pillow + pymupdf, once
python tools/render_pdf.py "paper.pdf" --info                                    # = pdfinfo
python tools/render_pdf.py "paper.pdf" pages_ --dpi 150 --first <first> --last <last>   # = pdftoppm
python tools/render_pdf.py "paper.pdf" --first <first> --last <last> --text paper.txt   # = pdftotext -layout
```

---

## 3. Identify the paper format

Two common vendor formats. Detect which one you have from a rendered page:

**A. SOLVED "digialm / FundaMakers" format** (used for CAT 2021 & 2022 here)
- Each MCQ shows options with a green ✓ on the correct one and red ✗ on the rest.
- TITA questions print `Possible Answer: <value>`.
- "Chosen Option" is the *candidate's* answer — **ignore it**, it is not the key.

**B. UNSOLVED "cracku"-style format** (used for CAT 2020 & 2017 here)
- No ticks. A separate **answer-key block** lists `QNo:- N , Correct Answer:- X`.
- For MCQ, X is a letter/number → convert to 0-based index. For TITA, X is the value.

---

## 4. Extracting answers

### Format A — green-tick detector
`tools/detect.py` scans the narrow left band where the ✓/✗ glyph sits (7–18 % of page width),
classifies each row as Green / Red, and returns the marks top-to-bottom.

```bash
python3 tools/detect.py page_042.png     # prints e.g. ['R','R','R','G']  → answer = index 3
```
- Clean single-question page ⇒ exactly **4 marks, one green**; the green's position (0-based)
  is the answer.
- If it returns **>4 marks or multiple greens** (long option text that is itself green-coloured,
  or two questions on one page), DO NOT trust it — open the page image and read the ✓ yourself.
- TITA answers come from the `Possible Answer:` text (via `pdftotext`), not the detector.

**Verification discipline:** trust the detector only on clean 4-mark/1-green pages. Vision-verify
every ambiguous page. When you're unsure, vision always wins.

### Format B — answer key
Parse the key block with a regex like `QNo:-\s*(\d+)\s*,\s*Correct Answer:-\s*([A-D0-9.\-]+)`.
Map MCQ letter→index (A/1→0, B/2→1, …). Keep TITA value as a string. Cross-check the count of
keys equals the number of questions.

---

## 5. Figures, tables, math

- **Figures** (charts, diagrams, Gantt/bar/pie): crop from the rendered page with Pillow,
  auto-trim whitespace, pad ~8px, save to `img/pyq/<year>/<slot>/<name>.png`. Reference in the
  context/question HTML as `<div class="qfig"><img loading="lazy" src="img/pyq/…png" alt="…"></div>`.
  See `tools/crop_figure.py` for a reusable helper. Keep crops tight — no stray captions.
- **Tables**: reconstruct as real HTML `<table>` (headers in `<th>`, cells in `<td>`). Do **not**
  flatten to `<br>`-separated text — the app styles real tables. Read numbers off the page image
  to avoid extraction errors.
- **Math**: transcribe to Unicode / minimal HTML. Use `<sup>`/`<sub>` for exponents/indices,
  `√`, `×`, `÷`, `−` (minus, not hyphen), `≤ ≥ ≠`, `₹`, fractions as `a/b`. Escape `<`, `>` and
  use `&lt; &gt;` inside option/stem text when comparing values (e.g. `x &lt; 5`).

---

## 6. Topic tagging (every question needs a `sub`)

The custom-test pool groups by `sub`. Assign a real topic to **every** question.

**VARC — tag by question type**
- Any question attached to a reading passage → `"Reading Comprehension"`.
- Standalone verbal: `"Para-jumble"` (sentences to sequence), `"Para-summary"` (four alternate
  summaries), `"Odd One Out"` (five jumbled, pick the odd), `"Para-completion"` (missing sentence).

**DILR — tag the SET, all its questions inherit one bucket**
`"Tables & Data Sets"`, `"Venn Diagrams & Set Theory"`, `"Games & Tournaments"`,
`"Networks & Routes"`, `"Grid & Arrangements"`, `"Sequencing & Scheduling"`,
`"Selection & Distribution"`, `"Conditional Logic & Puzzles"`.

**QA — finest subtopic that fits the stem.** Use the vocabulary already in `DATA.subs` inside
`index.html`, e.g.: Percentages, Profit & Loss, SI & CI, Averages, Alligation & Mixture, Ratio,
Time & Work, Time Speed Distance, Simple Equations, Quadratic Equations, Inequalities,
Logarithms, Functions, Sequence & Series, Arithmetic/Geometric Progression, Indices & Surds,
Permutations & Combinations, Probability, Triangles, Circles, Quadrilaterals, Mensuration,
Remainders, Factors, HCF & LCM, Numbers Basics, Base Systems.

(See `INGEST_NOTES.md` for the same list — keep them in sync.)

---

## 7. Assemble → validate → commit

1. Build the mock object; append to `mocks.json` (preserve existing entries; write with
   `ensure_ascii=False`).
2. Run the schema/tag validator:
   ```bash
   python3 tools/validate.py
   ```
   Fix every reported issue (empty opts, bad `ans`, out-of-range `c`, missing `sub`).
3. Run the headless load test (parses the real `index.html` + `mocks.json` in jsdom):
   ```bash
   node tools/smoke_test.js
   ```
   Expect `REAL ERRORS: 0`. (A single `localStorage is not available for opaque origins`
   line is a jsdom quirk and is ignored by the script.)
4. Commit with a descriptive message, e.g.
   `CAT 2023 Slot 1 full mock (VARC 24 + DILR 20 + QA 22) + figures`.

---

## 8. Per-question checklist (do this for every question)

- [ ] Stem transcribed correctly (math in Unicode, entities escaped).
- [ ] MCQ: 4 options, `ans` index verified from ✓ / key (vision-checked if ambiguous).
- [ ] TITA: `ans` string from `Possible Answer` / key.
- [ ] `c` points at the right passage/set context (or null).
- [ ] Figure cropped & referenced, or table rebuilt as HTML, if the question needs it.
- [ ] `sub` topic assigned per §6.

## 9. Common mistakes to avoid

- Using "Chosen Option" as the answer (it's the candidate's response, not the key).
- Trusting the detector on multi-question or long-green-option pages.
- Flattening tables to `<br>` text.
- Off-by-one `ctxs` indices after concatenating VARC + DILR contexts.
- Forgetting `sub`, or inventing a topic name not in the taxonomy.
- Hyphen `-` instead of true minus `−` in negative numbers/options.
