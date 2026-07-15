-- Read-only checks. Secret values must never appear in SQL results or logs.

select
    exists (
        select 1
        from vault.secrets
        where name = 'jamkkan_github_actions_token'
    ) as github_token_present;

select
    jobid,
    jobname,
    schedule,
    active
from cron.job
where jobname = 'jamkkan-news-collection';

select
    status,
    start_time,
    end_time
from cron.job_run_details
where jobid = (
    select jobid
    from cron.job
    where jobname = 'jamkkan-news-collection'
)
order by start_time desc
limit 10;
