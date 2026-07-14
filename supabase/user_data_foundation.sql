-- Sprint 07 foundation only. This creates new empty tables and never reads,
-- updates, deletes, or backfills the existing interests/settings/growth tables.

begin;

create table if not exists public.user_interests (
    owner_id text not null check (owner_id ~ '^usr_[0-9a-f]{64}$'),
    interest text not null check (char_length(interest) between 1 and 100),
    position smallint not null check (position between 0 and 4),
    primary key (owner_id, interest),
    unique (owner_id, position)
);

create table if not exists public.user_settings (
    owner_id text not null check (owner_id ~ '^usr_[0-9a-f]{64}$'),
    setting_key text not null check (char_length(setting_key) between 1 and 100),
    setting_value jsonb not null,
    primary key (owner_id, setting_key)
);

create table if not exists public.user_growth_daily (
    owner_id text not null check (owner_id ~ '^usr_[0-9a-f]{64}$'),
    activity_date date not null,
    articles integer not null default 0 check (articles >= 0),
    seconds integer not null default 0 check (seconds >= 0),
    read_news_ids text[] not null default '{}',
    primary key (owner_id, activity_date)
);

create table if not exists public.user_events (
    id uuid primary key,
    owner_id text not null check (owner_id ~ '^usr_[0-9a-f]{64}$'),
    event_type text not null check (char_length(event_type) between 1 and 100),
    news_id text,
    category text not null default '기타',
    title text not null default '',
    seconds integer not null default 0 check (seconds >= 0),
    occurred_at timestamptz not null
);

create index if not exists user_events_owner_occurred_idx
    on public.user_events (owner_id, occurred_at);

create or replace function public.replace_user_interests(
    p_owner_id text,
    p_interests text[]
)
returns void
language plpgsql
security invoker
set search_path = ''
as $$
begin
    if p_owner_id !~ '^usr_[0-9a-f]{64}$' then
        raise exception 'invalid owner id';
    end if;
    if cardinality(p_interests) > 5 then
        raise exception 'at most five interests are allowed';
    end if;

    delete from public.user_interests
    where owner_id = p_owner_id;

    insert into public.user_interests (owner_id, interest, position)
    select p_owner_id, interest, ordinal_position - 1
    from unnest(p_interests) with ordinality
        as selected(interest, ordinal_position);
end;
$$;

alter table public.user_interests enable row level security;
alter table public.user_settings enable row level security;
alter table public.user_growth_daily enable row level security;
alter table public.user_events enable row level security;

alter table public.user_interests force row level security;
alter table public.user_settings force row level security;
alter table public.user_growth_daily force row level security;
alter table public.user_events force row level security;

revoke all on public.user_interests from public, anon, authenticated;
revoke all on public.user_settings from public, anon, authenticated;
revoke all on public.user_growth_daily from public, anon, authenticated;
revoke all on public.user_events from public, anon, authenticated;

grant select, insert, update, delete on public.user_interests to service_role;
grant select, insert, update, delete on public.user_settings to service_role;
grant select, insert, update, delete on public.user_growth_daily to service_role;
grant select, insert, update, delete on public.user_events to service_role;

revoke all on function public.replace_user_interests(text, text[])
    from public, anon, authenticated;
grant execute on function public.replace_user_interests(text, text[])
    to service_role;

commit;
