-- GRE Practice Centre: one table of finished attempts, each row visible only to its owner.
-- Paste into Supabase: SQL Editor -> New query -> Run.
create table if not exists public.attempts (
  user_id uuid not null default auth.uid() references auth.users on delete cascade,
  id text not null,
  data jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);
alter table public.attempts enable row level security;
drop policy if exists "own rows" on public.attempts;
create policy "own rows" on public.attempts for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
grant select, insert, update, delete on public.attempts to authenticated;
revoke all on public.attempts from anon;
