# The prompt to paste into Antigravity

Copy everything in the box below into Antigravity's agent chat (Agent Manager → new task)
after you've opened the repo as your workspace. Adjust the "papers I'm giving you" list to
match whatever PDFs you actually drop in.

---

```
You are working in my repo: https://github.com/avirajbhatia13/percentile99
(a static CAT-prep web app). Clone it if it isn't already open, and work on a branch.

## Your mission
Ingest the CAT question papers I'm giving you into the app's question bank
(`mocks.json`) — paper by paper, slot by slot — so they appear as playable full mock
tests in the app, with verified answers, figures, tables and topic tags.

## Before you write a single line, read these (they are the spec):
1. `AGENTS.md`                       — project guide + non-negotiable guardrails
2. `docs/INGEST_FRAMEWORK.md`        — THE authoritative ingestion spec (schema, answer
                                        extraction, figures/tables/math, topic taxonomy)
3. `INGEST_NOTES.md`                 — the topic-tag vocabulary
4. `.agents/rules/cat-ingestion.md`  — the workspace rule
Then look at an existing mock in `mocks.json` (e.g. `cat2022slot1`) so you can copy its
exact shape.

## Environment setup (run once, in the terminal)
brew install poppler node
pip3 install pillow --break-system-packages
npm install jsdom

## Already ingested — DO NOT redo these
CAT 2017 Slot I, II · CAT 2020 Slot I, II, III · CAT 2021 Slot 1, 2, 3 ·
CAT 2022 Slot 1, 2, 3   (11 mocks, 787 questions)

## Papers I'm giving you
The PDFs are in `papers/` in the repo. Ingest every paper that is NOT in the list above.

## How to work — IMPORTANT
Work in units of ONE SLOT at a time (one slot ≈ 66 questions = VARC + DILR + QA).
For each slot, complete this loop fully before starting the next:

  1. PLAN    — tell me which paper/slot you're doing, its page ranges per section,
               and whether it's a solved (green-tick) or unsolved (answer-key) PDF.
  2. EXTRACT — render pages at 150 DPI (`pdftoppm`) and pull text (`pdftotext -layout`).
  3. ANSWERS — solved PDFs: `python3 tools/detect.py <page>.png` for MCQs and the
               "Possible Answer:" text for TITA. The detector is ONLY trustworthy when a
               page returns exactly 4 marks with exactly 1 green — for ANY other result,
               open the page image and read the ✓ with your own vision.
               Unsolved PDFs: parse the answer-key block; map MCQ letter → 0-based index.
               NEVER use "Chosen Option" — that's the candidate's answer, not the key.
  4. ASSETS  — crop figures with `python3 tools/crop_figure.py` into
               `img/pyq/<year>/<slot>/`; rebuild tables as real HTML <table>;
               transcribe math to Unicode (√ × − ≤, <sup>/<sub>).
  5. TAG     — give EVERY question a `sub` topic (VARC by question type, DILR one bucket
               per set, QA fine-grained subtopic) per the framework's taxonomy.
  6. ASSEMBLE— append the mock object to `mocks.json` (never rewrite existing entries;
               write with ensure_ascii=False). VARC passages fill `ctxs` first, then DILR
               set contexts; each question's `c` indexes into that flat array.
  7. VERIFY  — both must be clean:
                 python3 tools/validate.py      → "OK"
                 node tools/smoke_test.js       → "REAL ERRORS: 0"
  8. REPORT  — before committing, show me:
                 • the detector output summary and WHICH pages you vision-checked
                 • the answer key you derived (question number → answer)
                 • any question you were unsure about
  9. COMMIT  — one commit per slot, e.g.
                 "CAT 2023 Slot 1 full mock (VARC 24 + DILR 20 + QA 22) + figures"
Then move to the next slot. Pause and ask me if anything is genuinely ambiguous.

## Hard rules (do not break these)
- NEVER invent or guess an answer, option, number or figure. Everything comes from the PDF.
  If the tooling is ambiguous, READ THE PAGE IMAGE. Correctness beats speed — a wrong
  answer key is worse than a missing paper.
- Only modify `mocks.json` and add files under `img/`. Do NOT edit `index.html` or any
  app JavaScript.
- Append to `mocks.json`; preserve all existing mocks.
- Every question needs a non-empty `sub` topic tag.
- Use ids of the form `cat<year>slot<n>` (lowercase), `secMin: 40`, sections in the order
  VARC → DILR → QA.

## Definition of done (for the whole job)
- Every supplied paper is in `mocks.json` as one mock per slot.
- `python3 tools/validate.py` prints OK with the new higher question count.
- `node tools/smoke_test.js` prints REAL ERRORS: 0 and lists all mocks.
- Figures exist under `img/pyq/...` and every referenced image resolves.
- One clean commit per slot, pushed to a branch, with a summary of what you added and a
  list of anything you flagged as uncertain.

Start by reading the docs and giving me your plan for the first paper. Don't start
extracting until you've shown me the plan.
```

---

## After it finishes each slot — your 2-minute check

1. Open the PDF and spot-check **5 answers** against the diff (weight toward DILR — that's
   the section where mistakes have historically slipped through).
2. Confirm it printed `REAL ERRORS: 0`.
3. Confirm the diff touches only `mocks.json` and `img/` — if it edited `index.html`, revert that.
4. Merge the branch and `git push`. Vercel redeploys automatically.
