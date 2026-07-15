-- Roll back only the Jamkkan scheduler. Keep shared extensions installed and
-- remove `jamkkan_github_actions_token` separately in the Vault UI.

begin;

select cron.unschedule(jobid)
from cron.job
where jobname = 'jamkkan-news-collection';

commit;
