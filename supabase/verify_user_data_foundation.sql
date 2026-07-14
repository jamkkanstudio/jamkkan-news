-- Read-only post-apply checks. Every returned boolean must be true and every
-- user table must still be empty before USER_DATA_ENABLED is turned on.

with expected_tables(table_name) as (
    values
        ('user_interests'),
        ('user_settings'),
        ('user_growth_daily'),
        ('user_events')
)
select expected_tables.table_name,
       tables.relrowsecurity as rls_enabled,
       tables.relforcerowsecurity as rls_forced,
       not has_table_privilege('anon', tables.oid, 'select,insert,update,delete')
           as anon_blocked,
       not has_table_privilege(
           'authenticated', tables.oid, 'select,insert,update,delete'
       ) as authenticated_blocked,
       has_table_privilege('service_role', tables.oid, 'select')
       and has_table_privilege('service_role', tables.oid, 'insert')
       and has_table_privilege('service_role', tables.oid, 'update')
       and has_table_privilege('service_role', tables.oid, 'delete')
           as service_role_allowed
from expected_tables
join pg_class as tables
  on tables.relname = expected_tables.table_name
join pg_namespace as schemas
  on schemas.oid = tables.relnamespace
 and schemas.nspname = 'public'
order by expected_tables.table_name;

select 'user_events' as table_name, count(*) as row_count
from public.user_events
union all
select 'user_growth_daily', count(*) from public.user_growth_daily
union all
select 'user_interests', count(*) from public.user_interests
union all
select 'user_settings', count(*) from public.user_settings
order by table_name;

select
    not has_function_privilege(
        'anon', 'public.replace_user_interests(text,text[])', 'execute'
    ) as anon_rpc_blocked,
    not has_function_privilege(
        'authenticated',
        'public.replace_user_interests(text,text[])',
        'execute'
    ) as authenticated_rpc_blocked,
    has_function_privilege(
        'service_role',
        'public.replace_user_interests(text,text[])',
        'execute'
    ) as service_role_rpc_allowed;
