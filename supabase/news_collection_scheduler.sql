-- Sprint 10 operational scheduler.
-- Before applying, create one Vault secret named
-- `jamkkan_github_actions_token` in the Supabase Dashboard. Never paste the
-- secret into this file, SQL history, Git, logs, or chat.

begin;

create extension if not exists pg_cron;
create extension if not exists pg_net;

do $$
begin
    if not exists (
        select 1
        from vault.secrets
        where name = 'jamkkan_github_actions_token'
    ) then
        raise exception 'required Vault secret is missing';
    end if;
end;
$$;

select cron.unschedule(jobid)
from cron.job
where jobname = 'jamkkan-news-collection';

select cron.schedule(
    'jamkkan-news-collection',
    '7,17,27,37,47,57 * * * *',
    $job$
    select net.http_post(
        url := 'https://api.github.com/repos/jamkkanstudio/jamkkan-news/actions/workflows/collect-news.yml/dispatches',
        headers := jsonb_build_object(
            'Accept', 'application/vnd.github+json',
            'Authorization', 'Bearer ' || (
                select decrypted_secret
                from vault.decrypted_secrets
                where name = 'jamkkan_github_actions_token'
            ),
            'Content-Type', 'application/json',
            'User-Agent', 'jamkkan-supabase-cron',
            'X-GitHub-Api-Version', '2022-11-28'
        ),
        body := jsonb_build_object(
            'ref', 'main',
            'inputs', jsonb_build_object(
                'trigger_source', 'supabase-cron'
            )
        )
    ) as request_id;
    $job$
);

commit;
