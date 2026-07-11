# Percentile99 — Go-Live Guide

Three stages. Stage 1 puts the site live today. Stages 2–3 add Google login + cloud sync.

---

## Stage 1 · Deploy to Vercel (5 minutes)

This folder is a complete static site (`index.html`, `mocks.json`, `vercel.json`).

Open Terminal and run:

```bash
cd "<path to this percentile99-site folder>"
npx vercel login        # first time only — opens browser, log in
npx vercel --prod       # accept defaults; project name: percentile99
```

That's it — you get `https://percentile99.vercel.app` (or similar). Every future
update: run `npx vercel --prod` again from this folder.

Alternative without CLI: push this folder to a GitHub repo → vercel.com → Add New
Project → Import the repo → Deploy. (This also gives you auto-deploy on every
commit — recommended once real users arrive.)

---

## Stage 2 · Create the database (Supabase, ~10 minutes)

1. Go to **supabase.com** → New project (free tier). Name: `percentile99`.
   Region: `ap-south-1 (Mumbai)` — closest to your users.
2. In the dashboard: **SQL Editor → New query** → paste the entire contents of
   `schema.sql` (in this folder) → Run. This creates profiles, progress, stars,
   notes, attempts, imported-PYQ tables with row-level security (each user can
   only ever read/write their own rows) and auto-creates a profile on signup.
3. Note down from **Project Settings → API**:
   - `Project URL` (like `https://abcd1234.supabase.co`)
   - `anon public` key (this one is safe to put in frontend code — do NOT use
     the `service_role` key anywhere in the site)

---

## Stage 3 · Google login (~15 minutes)

1. **console.cloud.google.com** → create project `percentile99` →
   **APIs & Services → OAuth consent screen**: External, app name Percentile99,
   add your email; scopes: just the default (email, profile).
2. **Credentials → Create credentials → OAuth Client ID → Web application**:
   - Authorized JavaScript origins: `https://<your-site>.vercel.app`
   - Authorized redirect URI: `https://<your-supabase-project>.supabase.co/auth/v1/callback`
3. Copy the **Client ID** and **Client Secret**.
4. Supabase dashboard → **Authentication → Providers → Google** → enable, paste
   Client ID + Secret → Save.
5. Supabase → **Authentication → URL Configuration** → Site URL =
   `https://<your-site>.vercel.app`.

---

## Stage 4 · Hand back to Claude

Paste into the chat:
- your live Vercel URL
- your Supabase Project URL
- the `anon public` key

Claude then wires the app: real "Continue with Google" button, cloud sync of
progress/stars/notes/attempts (with localStorage as offline cache), multi-device
support — and redeploys via `npx vercel --prod`.

## Notes for running this for real users

- **Free-tier limits**: Vercel hobby (100 GB bandwidth/mo) and Supabase free
  (500 MB DB, 50k monthly active users) comfortably cover thousands of students.
- **Custom domain**: buy one (e.g. percentile99.in) and add it in Vercel →
  Project → Domains; then update the Google OAuth origins + Supabase Site URL.
- **Legal**: the mock bank contains actual CAT questions (IIM copyright). Fine
  for personal study; for a public product you should either keep the mock
  section private/invite-only, seek permission, or replace with original
  questions. The 24 starter drill questions are original and safe.
- **Analytics**: enable Vercel Analytics in the dashboard (free) to see usage.
