-- Dineren & Slapen: opslag voor reviews, berichten en nieuwsbriefinschrijvingen.
-- Draai dit één keer in de SQL-editor van Supabase. Het script mag opnieuw gedraaid worden.
--
-- Beveiligingsmodel
--  * Bezoekers (rol anon) mogen alleen INVOEGEN, en alleen in de kolommen die het formulier vult.
--    Ze kunnen niets lezen, wijzigen of verwijderen.
--  * Goedgekeurde reviews zijn alleen leesbaar via de functie approved_reviews(), zonder e-mailadres.
--  * Alleen ingelogde gebruikers wier e-mailadres in public.admins staat, kunnen lezen en beheren.
--  * Elke inzending krijgt een gehashte vingerafdruk van het IP-adres; meer dan 5 per uur wordt geweigerd.

create extension if not exists pgcrypto with schema extensions;

-- ---------- beheerders ----------
create table if not exists public.admins (
  email text primary key check (email = lower(email))
);
alter table public.admins enable row level security;
revoke all on public.admins from anon, authenticated;
-- geen policies: de lijst is alleen via de functie hieronder te raadplegen

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((auth.jwt() ->> 'email') is not null
    and exists (select 1 from public.admins a where a.email = lower(auth.jwt() ->> 'email')), false)
$$;
revoke all on function public.is_admin() from public, anon;
grant execute on function public.is_admin() to authenticated;

-- ---------- vingerafdruk en spamrem ----------
create or replace function public.client_fp() returns text
language sql stable as $$
  select encode(extensions.digest(
    coalesce(
      nullif(current_setting('request.headers', true)::json ->> 'cf-connecting-ip', ''),
      nullif(split_part(current_setting('request.headers', true)::json ->> 'x-forwarded-for', ',', 1), ''),
      'onbekend') || '|dineren-en-slapen', 'sha256'), 'hex')
$$;
revoke all on function public.client_fp() from public, anon, authenticated;

create or replace function public.guard_insert() returns trigger
language plpgsql security definer set search_path = public as $$
declare n int;
begin
  new.fp := public.client_fp();
  new.created_at := now();
  execute format('select count(*) from public.%I where fp = $1 and created_at > now() - interval ''1 hour''', tg_table_name)
    into n using new.fp;
  if n >= 5 and not public.is_admin() then
    raise exception 'Te veel inzendingen, probeer het later opnieuw' using errcode = 'P0001';
  end if;
  if tg_table_name = 'reviews' then
    new.status := 'nieuw'; new.note := null; new.reviewed_at := null;
  elsif tg_table_name = 'messages' then
    new.status := 'nieuw'; new.note := null; new.handled_at := null;
  elsif tg_table_name = 'subscribers' then
    new.email := lower(btrim(new.email)); new.status := 'actief'; new.unsubscribed_at := null;
  end if;
  return new;
end $$;
revoke all on function public.guard_insert() from public, anon, authenticated;

-- ---------- reviews ----------
create table if not exists public.reviews (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  loc_id text not null check (loc_id ~ '^[a-z0-9-]{2,80}$'),
  loc_name text not null check (char_length(loc_name) between 2 and 120),
  name text not null check (char_length(btrim(name)) between 2 and 60),
  email text check (email is null or (char_length(email) <= 200 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')),
  visit_month text check (visit_month is null or visit_month ~ '^20[0-9]{2}-(0[1-9]|1[0-2])$'),
  score_e smallint not null check (score_e between 1 and 10),
  score_s smallint not null check (score_s between 1 and 10),
  score_p smallint not null check (score_p between 1 and 10),
  body text not null check (char_length(btrim(body)) between 40 and 3000),
  visited boolean not null check (visited),
  lang text not null default 'nl' check (lang in ('nl', 'en')),
  status text not null default 'nieuw' check (status in ('nieuw', 'goedgekeurd', 'afgewezen')),
  note text check (note is null or char_length(note) <= 1000),
  reviewed_at timestamptz,
  fp text
);
create index if not exists reviews_status_idx on public.reviews (status, created_at desc);
create index if not exists reviews_loc_idx on public.reviews (loc_id, status);

-- ---------- berichten: contactformulier en tips ----------
create table if not exists public.messages (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('contact', 'tip')),
  name text check (name is null or char_length(btrim(name)) between 1 and 80),
  email text check (email is null or (char_length(email) <= 200 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')),
  subject text check (subject is null or char_length(subject) <= 120),
  address_name text check (address_name is null or char_length(address_name) <= 160),
  address_place text check (address_place is null or char_length(address_place) <= 120),
  province text check (province is null or char_length(province) <= 40),
  body text check (body is null or char_length(body) <= 5000),
  page text check (page is null or char_length(page) <= 200),
  status text not null default 'nieuw' check (status in ('nieuw', 'beantwoord', 'gearchiveerd')),
  note text check (note is null or char_length(note) <= 1000),
  handled_at timestamptz,
  fp text,
  constraint contact_needs_email_and_text check (kind = 'tip' or (email is not null and char_length(btrim(coalesce(body, ''))) >= 5)),
  constraint tip_needs_address check (kind = 'contact' or char_length(btrim(coalesce(address_name, ''))) >= 2)
);
create index if not exists messages_status_idx on public.messages (status, created_at desc);

-- ---------- nieuwsbrief ----------
create table if not exists public.subscribers (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  email text not null check (char_length(email) <= 200 and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'),
  source text check (source is null or char_length(source) <= 200),
  lang text not null default 'nl' check (lang in ('nl', 'en')),
  status text not null default 'actief' check (status in ('actief', 'afgemeld')),
  unsubscribed_at timestamptz,
  fp text
);
create unique index if not exists subscribers_email_key on public.subscribers (lower(email));

-- ---------- triggers ----------
drop trigger if exists reviews_guard on public.reviews;
create trigger reviews_guard before insert on public.reviews for each row execute function public.guard_insert();
drop trigger if exists messages_guard on public.messages;
create trigger messages_guard before insert on public.messages for each row execute function public.guard_insert();
drop trigger if exists subscribers_guard on public.subscribers;
create trigger subscribers_guard before insert on public.subscribers for each row execute function public.guard_insert();

-- ---------- rechten: eerst alles dicht, dan precies openzetten ----------
alter table public.reviews enable row level security;
alter table public.messages enable row level security;
alter table public.subscribers enable row level security;

revoke all on public.reviews, public.messages, public.subscribers from anon, authenticated;

grant insert (loc_id, loc_name, name, email, visit_month, score_e, score_s, score_p, body, visited, lang) on public.reviews to anon, authenticated;
grant insert (kind, name, email, subject, address_name, address_place, province, body, page) on public.messages to anon, authenticated;
grant insert (email, source, lang) on public.subscribers to anon, authenticated;

grant select, delete on public.reviews, public.messages, public.subscribers to authenticated;
grant update (status, note, reviewed_at) on public.reviews to authenticated;
grant update (status, note, handled_at) on public.messages to authenticated;
grant update (status, unsubscribed_at) on public.subscribers to authenticated;

do $$
declare t text;
begin
  foreach t in array array['reviews', 'messages', 'subscribers'] loop
    execute format('drop policy if exists %I on public.%I', t || '_insert', t);
    execute format('drop policy if exists %I on public.%I', t || '_admin_select', t);
    execute format('drop policy if exists %I on public.%I', t || '_admin_update', t);
    execute format('drop policy if exists %I on public.%I', t || '_admin_delete', t);
    execute format('create policy %I on public.%I for insert to anon, authenticated with check (status = %L)', t || '_insert', t, case t when 'subscribers' then 'actief' else 'nieuw' end);
    execute format('create policy %I on public.%I for select to authenticated using (public.is_admin())', t || '_admin_select', t);
    execute format('create policy %I on public.%I for update to authenticated using (public.is_admin()) with check (public.is_admin())', t || '_admin_update', t);
    execute format('create policy %I on public.%I for delete to authenticated using (public.is_admin())', t || '_admin_delete', t);
  end loop;
end $$;

-- ---------- openbaar: goedgekeurde reviews per adres, zonder e-mailadres ----------
create or replace function public.approved_reviews(p_loc text)
returns table (name text, visit_month text, score_e smallint, score_s smallint, score_p smallint, body text, created_at timestamptz)
language sql stable security definer set search_path = public as $$
  select btrim(r.name), r.visit_month, r.score_e, r.score_s, r.score_p, r.body, r.created_at
  from public.reviews r
  where r.status = 'goedgekeurd' and r.loc_id = p_loc
  order by r.created_at desc
  limit 50
$$;
revoke all on function public.approved_reviews(text) from public;
grant execute on function public.approved_reviews(text) to anon, authenticated;

-- ---------- beheerder ----------
-- Vervang het adres als je met een ander e-mailadres inlogt.
insert into public.admins (email) values ('dinerenenslapen@gmail.com') on conflict do nothing;
