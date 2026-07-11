# Percentile99 · CAT Prep OS

A full CAT preparation platform: 469 mapped Rodha lectures with a self-adjusting
study planner, LeetCode-style activity heatmap, topic-tagged real CAT PYQs, timed
topic drills, and full-paper mocks with the authentic CAT interface (section
locks, palette, on-screen calculator, per-question analysis).

**Live stack:** static frontend (Vercel) + Supabase (Postgres, Google OAuth, RLS).

## Repository layout

```
index.html          The entire app (vanilla JS single-file, no build step)
mocks.json          5 real CAT papers (2017 Slots I–II, 2020 Slots I–III), 391 questions
vercel.json         Static hosting config
supabase/schema.sql Database schema: profiles, progress, stars, notes, attempts + RLS
docs/SETUP_GUIDE.md Step-by-step: Vercel deploy, Supabase, Google OAuth
pipeline/           Data provenance — scripts that built everything:
  build_plan.py         playlist data → 69-day schedule (plan_data.json)
  parse_papers.py       CAT paper PDFs → structured mocks JSON
  build_dashboard_v6.py app assembler (embeds data into index.html)
  build_site_lite.py    site splitter (externalises mocks.json)
  qids.txt / dids.txt   YouTube video IDs (verified against durations)
  bank.json             24 original CAT-style drill questions
```

## Develop & deploy

No build step — edit `index.html`, open it locally, push to deploy (once the
repo is imported in Vercel, every push to `main` auto-deploys).

To regenerate `index.html` from data: `cd pipeline && python3 build_dashboard_v6.py`
(then re-run `build_site_lite.py` logic to externalise mocks).

## Data notes

- Lecture names/durations/IDs extracted from the official Rodha playlists
  (verified programmatically, July 2026).
- `mocks.json` contains actual CAT questions (IIM copyright). Fine for personal
  study; for a public product keep mocks private/invite-only or replace with
  original content. The 24 `bank.json` drill questions are original.
- 37 of 428 parsed questions were excluded (formulas/figures lost in PDF→text).

## Roadmap

- [ ] Supabase: Google sign-in + cloud sync (schema ready in `supabase/`)
- [ ] Export/backup of local progress
- [ ] Re-baseline button for slipped schedules + rest-day support
- [ ] Timestamp-based test timers (background-tab safe)
- [ ] VARC drills (tag mock VARC questions)
- [ ] Ingest remaining papers (2018–2022 pending answer keys; 2005–2016 legacy formats)
