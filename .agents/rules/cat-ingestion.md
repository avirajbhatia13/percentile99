# Workspace rule: CAT paper ingestion

This project's recurring task is turning CAT past-paper PDFs into mock tests in `mocks.json`.

Whenever the user asks to "ingest", "add", or "inject" a CAT paper:
- Read `docs/INGEST_FRAMEWORK.md` fully first — it is the authoritative spec.
- Follow its pipeline exactly; obey the guardrails in `AGENTS.md`.
- Never fabricate answers, options, figures or numbers — read the rendered page image when
  the tooling is ambiguous.
- Before committing, both of these must pass clean:
  - `python3 tools/validate.py`
  - `node tools/smoke_test.js`  → `REAL ERRORS: 0`
- Only edit `mocks.json` and add files under `img/`. Do not modify the app's JS (`index.html`)
  unless the user explicitly asks.
- Append to `mocks.json`; never rewrite existing mocks. One paper/slot per commit.
