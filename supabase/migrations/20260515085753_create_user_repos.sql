-- user_repos metadata registry for per-user Pinecone namespaces
-- Run in Supabase SQL Editor.

create table if not exists public.user_repos (
  user_id uuid not null,
  repo_name text not null,
  repo_url text not null,
  namespace text not null,
  chunk_count integer not null default 0,
  status text not null default 'ready',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),

  constraint user_repos_user_fk
    foreign key (user_id)
    references auth.users(id)
    on delete cascade,

  constraint user_repos_repo_name_not_blank
    check (char_length(trim(repo_name)) > 0),

  constraint user_repos_repo_url_not_blank
    check (char_length(trim(repo_url)) > 0),

  constraint user_repos_chunk_count_non_negative
    check (chunk_count >= 0),

  constraint user_repos_status_allowed
    check (status in ('ready', 'indexing', 'failed')),

  constraint user_repos_user_repo_unique unique (user_id, repo_name),
  constraint user_repos_namespace_unique unique (namespace)
);

create index if not exists idx_user_repos_user_id
  on public.user_repos (user_id);

create index if not exists idx_user_repos_namespace
  on public.user_repos (namespace);

create or replace function public.set_updated_at_user_repos()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_user_repos_set_updated_at on public.user_repos;
create trigger trg_user_repos_set_updated_at
before update on public.user_repos
for each row
execute function public.set_updated_at_user_repos();

alter table public.user_repos enable row level security;

-- Users can view only their own rows.
drop policy if exists user_repos_select_own on public.user_repos;
create policy user_repos_select_own
on public.user_repos
for select
using (auth.uid() = user_id);

-- Users can insert only rows tied to their own auth UID.
drop policy if exists user_repos_insert_own on public.user_repos;
create policy user_repos_insert_own
on public.user_repos
for insert
with check (auth.uid() = user_id);

-- Users can delete only their own rows.
drop policy if exists user_repos_delete_own on public.user_repos;
create policy user_repos_delete_own
on public.user_repos
for delete
using (auth.uid() = user_id);

-- Optional but useful for upsert/update paths.
drop policy if exists user_repos_update_own on public.user_repos;
create policy user_repos_update_own
on public.user_repos
for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);
