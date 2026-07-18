# Percentile99 · CAT Prep OS

A full CAT preparation platform: 469 mapped Rodha lectures with a self-adjusting
study planner, LeetCode-style activity heatmap (26-week rolling window + streaks),
topic-tagged real CAT PYQs, timed topic drills with a smart auto-select mode, notes
per question, and full-paper mocks with the authentic CAT interface (section locks,
palette, on-screen calculator, per-question analysis).

**Live stack:** static frontend (Vercel) + Supabase (Postgres, Google OAuth sign-in,
cloud sync, RLS) — auth and sync are live, not just scaffolded.

## Repository layout

```
index.html            The entire app (vanilla JS single-file, no build step)
mocks.json             11 real CAT papers (2017 Slots I–II, 2020 Slots I–III,
                        2021 Slots 1–3, 2022 Slots 1–3), 787 topic-tagged questions
vercel.json            Static hosting config
supabase/schema.sql    Database schema: profiles, progress, stars, notes, attempts + RLS
docs/SETUP_GUIDE.md    Step-by-step: Vercel deploy, Supabase, Google OAuth
docs/INGEST_FRAMEWORK.md  Spec for adding a new CAT paper (render → extract → tag → validate)
AGENTS.md              Cross-tool agent guide (Antigravity/Cursor/Claude Code) for paper ingestion
ANTIGRAVITY_SETUP.md   Google Antigravity setup for the ingestion workflow
INGEST_NOTES.md        Topic-tagging vocabulary (QA/DILR/VARC subtopics), kept in sync with the framework
tools/                 Ingestion + validation scripts:
  detect.py              green-tick answer-key detector
  crop_figure.py         figure extraction from paper PDFs
  validate.py            schema + tag + figure-path validation (`npm run validate`)
  smoke_test.js          headless app load check (`npm run smoke`)
pipeline/               Data provenance — scripts that built the original app:
  build_plan.py           playlist data → 69-day schedule (plan_data.json)
  parse_papers.py         CAT paper PDFs → structured mocks JSON
  build_dashboard_v6.py   app assembler (embeds data into index.html)
  build_site_lite.py      site splitter (externalises mocks.json)
  qids.txt / dids.txt     YouTube video IDs (verified against durations) — 469 total
  bank.json               24 original CAT-style drill questions
```

## Develop & deploy

No build step — edit `index.html`, open it locally, push to deploy (once the
repo is imported in Vercel, every push to `main` auto-deploys).

To regenerate `index.html` from data: `cd pipeline && python3 build_dashboard_v6.py`
(then re-run `build_site_lite.py` logic to externalise mocks).

To add a new CAT paper to `mocks.json`, follow `docs/INGEST_FRAMEWORK.md` and run
both checks before committing: `npm run validate` and `npm run smoke`.

## Data notes

- Lecture names/durations/IDs extracted from the official Rodha playlists
  (verified programmatically, July 2026).
- `mocks.json` contains actual CAT questions (IIM copyright). Fine for personal
  study; for a public product keep mocks private/invite-only or replace with
  original content. The 24 `bank.json` drill questions are original.
- Every question carries a topic (`sub`) tag; QA is fine-grained, DILR is tagged
  per set, VARC by question type — see `INGEST_NOTES.md` for the taxonomy. This
  powers the topic drill picker and the smart-test auto-select mode.

## Roadmap

- [ ] Export/backup of local progress
- [ ] Re-baseline button for slipped schedules + rest-day support
- [ ] Ingest remaining papers (2018–2019 pending answer keys; 2005–2016 legacy formats)
