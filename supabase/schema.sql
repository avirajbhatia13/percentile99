-- Percentile99 · Supabase schema (run in SQL Editor)
-- One row per user for profile/config; granular rows for progress items.

create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  name text,
  email text,
  target text default 'CAT 2026',
  hrs_week int default 30,
  plan_mode text default 'daily' check (plan_mode in ('daily','weekly','topic')),
  slot_min int default 75,
  slots int default 2 check (slots in (1,2)),
  start_date date default '2026-07-13',
  theme text default 'light',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- lecture completion: item_id like 'Q12' / 'L3'; done_on powers the heatmap
create table public.progress (
  user_id uuid references auth.users(id) on delete cascade,
  item_id text,
  done_on date not null default current_date,
  primary key (user_id, item_id)
);

create table public.stars (
  user_id uuid references auth.users(id) on delete cascade,
  item_id text,
  primary key (user_id, item_id)
);

create table public.notes (
  user_id uuid references auth.users(id) on delete cascade,
  item_id text,
  body text not null,
  updated_at timestamptz default now(),
  primary key (user_id, item_id)
);

-- test/mock attempts: summary columns + full detail as jsonb
create table public.attempts (
  id bigint generated always as identity primary key,
  user_id uuid references auth.users(id) on delete cascade,
  kind text not null check (kind in ('drill','mock')),
  taken_on date not null default current_date,
  n int, score int, correct int, wrong int, skipped int, secs int,
  label text,
  detail jsonb
);
create index attempts_user_idx on public.attempts(user_id, taken_on);

-- user-imported PYQ sets (per-user custom banks)
create table public.imported_pyqs (
  user_id uuid references auth.users(id) on delete cascade,
  qid text,
  q jsonb not null,
  primary key (user_id, qid)
);

-- ============ Row Level Security: users only touch their own rows ============
alter table public.profiles enable row level security;
alter table public.progress enable row level security;
alter table public.stars enable row level security;
alter table public.notes enable row level security;
alter table public.attempts enable row level security;
alter table public.imported_pyqs enable row level security;

create policy "own profile" on public.profiles for all
  using (auth.uid() = id) with check (auth.uid() = id);
create policy "own progress" on public.progress for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own stars" on public.stars for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own notes" on public.notes for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own attempts" on public.attempts for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "own pyqs" on public.imported_pyqs for all
  using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- auto-create profile row on signup (pulls name/email from Google)
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, name, email)
  values (new.id, coalesce(new.raw_user_meta_data->>'full_name',''), new.email)
  on conflict (id) do nothing;
  return new;
end $$;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
