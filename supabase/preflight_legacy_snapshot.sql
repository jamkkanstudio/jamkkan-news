-- Run before applying the user-data foundation. This is read-only and returns
-- counts plus content fingerprints; store the result in a protected ops record.
-- It never prints deployment secrets and never changes or assigns legacy rows.

select 'interests' as table_name,
       count(*) as row_count,
       md5(coalesce(jsonb_agg(to_jsonb(row_data)
           order by to_jsonb(row_data)::text)::text, '[]')) as content_fingerprint
from public.interests as row_data
union all
select 'settings', count(*),
       md5(coalesce(jsonb_agg(to_jsonb(row_data)
           order by to_jsonb(row_data)::text)::text, '[]'))
from public.settings as row_data
union all
select 'growth_daily', count(*),
       md5(coalesce(jsonb_agg(to_jsonb(row_data)
           order by to_jsonb(row_data)::text)::text, '[]'))
from public.growth_daily as row_data
union all
select 'events', count(*),
       md5(coalesce(jsonb_agg(to_jsonb(row_data)
           order by to_jsonb(row_data)::text)::text, '[]'))
from public.events as row_data
union all
select 'news', count(*),
       md5(coalesce(jsonb_agg(to_jsonb(row_data)
           order by to_jsonb(row_data)::text)::text, '[]'))
from public.news as row_data
order by table_name;
