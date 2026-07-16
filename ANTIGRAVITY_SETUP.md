# Ingesting CAT papers with Google Antigravity (Gemini)

You can hand the paper-ingestion work to Antigravity's Gemini agent instead of spending
Claude usage. This repo already ships everything the agent needs: an `AGENTS.md`, a workspace
rule, a skill, the spec (`docs/INGEST_FRAMEWORK.md`), and the tools. Antigravity reads these
automatically. Here's the one-time setup and the per-paper loop.

## One-time setup

1. **Install Antigravity.** Download from https://antigravity.google and sign in with your
   Google account (it's free during the public preview; Gemini 3 has generous limits).

2. **Open this repo as the workspace.** File → Open Folder → select your
   `percentile99` folder. Antigravity will pick up:
   - `AGENTS.md` (root) — cross-tool project guide,
   - `.agents/rules/cat-ingestion.md` — always-on workspace rule,
   - `.agents/skills/ingest-cat-paper/` — the ingestion skill.
   You can confirm/enable these under Agent Manager → ••• → Customizations.

3. **Install the local prerequisites** (Antigravity runs these in its terminal). On macOS:
   ```bash
   brew install poppler node        # pdftoppm / pdftotext / pdfinfo, and node
   pip3 install pillow --break-system-packages
   cd ~/Projects/percentile99 && npm install jsdom
   ```

4. **(Optional) A global rule for correctness.** Agent Manager → ••• → Customizations →
   + Global, and paste:
   > For CAT paper ingestion, never fabricate answers or figures. Verify every MCQ answer
   > from the paper; when the tick-detector is ambiguous, open the page image and read it.
   > Run `python3 tools/validate.py` and `node tools/smoke_test.js` before committing.

## Per-paper loop

1. Drop the paper PDF anywhere in the repo folder (e.g. a `papers/` subfolder).
2. In Antigravity's agent chat, prompt something like:
   > Ingest `papers/CAT-2023.pdf` into `mocks.json` following `docs/INGEST_FRAMEWORK.md`.
   > It has 3 slots — do **Slot 1 only** for now: VARC, DILR, QA. Verify every answer,
   > crop figures, tag topics, then run the validator and smoke test and show me the diff.
3. Let it work. It will render pages, read them (Gemini has vision for the ambiguous tick
   pages), crop figures, build the mock, and run the two checks.
4. **Review before you accept.** Skim the diff and spot-check ~5 answers against the PDF.
   Make sure `node tools/smoke_test.js` printed `REAL ERRORS: 0`.
5. Commit and push (Antigravity can do this, or you):
   ```bash
   git add -A && git commit -m "CAT 2023 Slot 1 full mock" && git push
   ```

## Tips that keep quality high & context small
- **One slot per task.** A full slot (~66 questions) is a good unit. Papers with 3 slots =
  3 tasks. This keeps the agent's context manageable and the diffs reviewable.
- **Make it show its work.** Ask it to print the detector output and which pages it
  vision-checked, so you can see where answers came from.
- **Trust but verify answers.** The tick-detector + vision pipeline is solid but not
  infallible; a 2-minute spot-check per slot catches the rare miss. The DILR section is the
  one most worth checking.
- **If it edits `index.html`,** stop it — ingestion should only touch `mocks.json` and `img/`.
- **Deploy** is just `git push`; Vercel redeploys automatically.

## What "good" looks like
- `python3 tools/validate.py` → `OK — N mocks, M questions checked`
- `node tools/smoke_test.js` → `REAL ERRORS: 0`, app lists every mock
- New figures present under `img/pyq/<year>/<slot>/`
- Every new question has a `sub` topic tag

That's it — the same pipeline that produced the 2017/2020/2021/2022 mocks, now runnable by
any agent, on any tool.
