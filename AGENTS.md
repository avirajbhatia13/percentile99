# AGENTS.md — percentile99

Cross-tool agent guide (read by Google Antigravity, Cursor, Claude Code, etc.).

## What this repo is
A single-file static web app for CAT (Indian MBA entrance) prep. No build step, no
framework. Deployed on Vercel from GitHub; Supabase handles auth/sync.

- `index.html` — the entire app (HTML + CSS + vanilla JS in one file).
- `mocks.json` — the question bank: an array of mock-test objects (real CAT past papers).
- `img/pyq/<year>/<slot>/` — figures (charts/diagrams) referenced by questions.
- `tools/` — ingestion + validation scripts.
- `docs/INGEST_FRAMEWORK.md` — **the spec for adding a new paper. Read it fully before ingesting.**
- `INGEST_NOTES.md` — the topic-tagging vocabulary (keep in sync with the framework).

## The one job you'll usually be asked to do: ingest a CAT paper
When the user gives you a CAT question-paper PDF and asks you to add it:

1. **Read `docs/INGEST_FRAMEWORK.md` end to end.** It is the source of truth.
2. Follow the pipeline: render → extract → determine answers → figures/tables/math →
   tag topics → assemble into `mocks.json` → validate → smoke-test → commit.
3. Run BOTH checks and get them clean before committing:
   ```bash
   python3 tools/validate.py      # schema + tags + figure paths
   node tools/smoke_test.js       # headless app load  (needs: npm i jsdom)
   ```

## Non-negotiable guardrails
- **Never invent data.** Every answer, option, figure and number must come from the PDF.
  If a tool is ambiguous, open the rendered page image and read it with vision.
- The green-tick detector (`tools/detect.py`) is trustworthy ONLY on pages that return
  exactly 4 marks with 1 green. Anything else → verify by eye.
- "Chosen Option" in solved PDFs is the candidate's answer, not the key. Ignore it.
- Every question must carry a real `sub` (topic) tag from the taxonomy in the framework.
- Preserve existing entries in `mocks.json` — append, don't rewrite.
- Keep tables as real HTML `<table>`; use true minus `−` and `<sup>/<sub>` for math.
- Do NOT touch `DATA.subs` in `index.html` or the app's JS unless explicitly asked; ingestion
  only edits `mocks.json` and adds files under `img/`.

## Verifying you didn't break the app
`node tools/smoke_test.js` must print `REAL ERRORS: 0`. The app must still list every mock.

## House style
Single-file app, no dependencies added to `index.html`. Small, reviewable commits, one
paper (or one slot) per commit, with a message like
`CAT 2023 Slot 1 full mock (VARC 24 + DILR 20 + QA 22) + figures`.
