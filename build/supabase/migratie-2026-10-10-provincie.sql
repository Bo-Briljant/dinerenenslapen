-- migratie 10 oktober 2026: voorkeursprovincie bij nieuwsbriefinschrijvingen
alter table public.subscribers add column if not exists province text;
alter table public.subscribers drop constraint if exists subscribers_province_check;
alter table public.subscribers add constraint subscribers_province_check check (province is null or province in
  ('groningen', 'friesland', 'drenthe', 'overijssel', 'flevoland', 'gelderland', 'utrecht', 'noord-holland', 'zuid-holland', 'zeeland', 'noord-brabant', 'limburg', 'geen'));
create index if not exists subscribers_province_idx on public.subscribers (province);
create or replace function public.guard_insert() returns trigger
language plpgsql security definer set search_path = '' as $$
declare n int; total int;
begin
  new.fp := public.client_fp();
  new.created_at := now();
  perform pg_advisory_xact_lock(hashtext('guard_' || tg_table_name));
  execute format('select count(*) filter (where fp = $1), count(*) from public.%I where created_at > now() - interval ''1 hour''', tg_table_name)
    into n, total using new.fp;
  if (n >= 5 or total >= 100) and not public.is_admin() then
    raise exception 'Te veel inzendingen, probeer het later opnieuw' using errcode = 'P0001';
  end if;
  if tg_table_name = 'reviews' then
    new.status := 'nieuw'; new.note := null; new.reviewed_at := null;
  elsif tg_table_name = 'messages' then
    new.status := 'nieuw'; new.note := null; new.handled_at := null;
  elsif tg_table_name = 'subscribers' then
    new.email := lower(btrim(new.email)); new.status := 'actief'; new.unsubscribed_at := null;
    -- bestaat het adres al, dan stil overslaan: zo verraadt de site niet wie er ingeschreven staat
    -- wel de nieuwste voorkeursprovincie bijwerken
    if exists (select 1 from public.subscribers s where lower(s.email) = new.email) then
      if new.province is not null then update public.subscribers s set province = new.province where lower(s.email) = new.email; end if;
      return null;
    end if;
  end if;
  return new;
end $$;
revoke all on function public.guard_insert() from public, anon, authenticated;
grant insert (email, source, lang, province) on public.subscribers to anon, authenticated;
grant update (status, unsubscribed_at, province) on public.subscribers to authenticated;
notify pgrst, 'reload schema';
select column_name from information_schema.columns where table_schema = 'public' and table_name = 'subscribers' order by ordinal_position;
