-- Run this in Supabase Dashboard > SQL Editor for the Pendo project.
create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  display_name text,
  plan text not null default 'Free' check (plan in ('Free','Plus','Premium')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.app_records (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  record_type text not null check (record_type in ('task','event','bill','list','document','goal','note')),
  content jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists app_records_user_type_created_idx
  on public.app_records(user_id, record_type, created_at desc);


alter table public.profiles enable row level security;
alter table public.app_records enable row level security;

-- Users may only access their own profile and their own app data.
drop policy if exists "profile_select_own" on public.profiles;
create policy "profile_select_own" on public.profiles for select using (auth.uid() = id);
drop policy if exists "profile_insert_own" on public.profiles;
create policy "profile_insert_own" on public.profiles for insert with check (auth.uid() = id);
drop policy if exists "profile_update_own" on public.profiles;
create policy "profile_update_own" on public.profiles for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "records_select_own" on public.app_records;
create policy "records_select_own" on public.app_records for select using (auth.uid() = user_id);
drop policy if exists "records_insert_own" on public.app_records;
create policy "records_insert_own" on public.app_records for insert with check (auth.uid() = user_id);
drop policy if exists "records_update_own" on public.app_records;
create policy "records_update_own" on public.app_records for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "records_delete_own" on public.app_records;
create policy "records_delete_own" on public.app_records for delete using (auth.uid() = user_id);

-- Create profile automatically when a user signs up.
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, coalesce(new.raw_user_meta_data->>'display_name', split_part(new.email, '@', 1)))
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
for each row execute procedure public.handle_new_user();

-- Prevent normal authenticated clients from changing subscription entitlements.
-- Only trusted server-side code (where auth.uid() is NULL, e.g. service role) may change plan.
create or replace function public.prevent_client_plan_change()
returns trigger language plpgsql as $$
begin
  if auth.uid() = old.id and new.plan is distinct from old.plan then
    raise exception 'Subscription plan can only be changed by trusted billing logic';
  end if;
  return new;
end;
$$;

drop trigger if exists protect_profile_plan on public.profiles;
create trigger protect_profile_plan before update on public.profiles
for each row execute procedure public.prevent_client_plan_change();
