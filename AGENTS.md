# Jamkkan working agreement

`docs/PROJECT_CONTEXT.md` is the architecture baseline, `ROADMAP.md` is the priority source, and the latest file in `docs/sprints/` is the execution baseline.

## Sprint start

1. Start each Sprint in a new Codex task and rename it `Sprint NN — concise goal`.
2. Read this file, `docs/PROJECT_CONTEXT.md`, `ROADMAP.md`, and the latest Sprint record before inspecting code. Read other documents only when the request or discovered scope requires them.
3. Fetch `origin/main`, confirm local `main` is current and clean, then state scope, exclusions, and data-preservation rules.
4. Use `rg` to locate relevant code before reading whole files. Avoid broad output that will be truncated or need rereading.

## Non-negotiable safety

- Keep public reading and the legacy growth-record flow working without login or secrets.
- Require deployment `ADMIN_EMAILS` at page and service boundaries for every global content or setting write.
- Never commit or print OAuth, Supabase, GitHub, AI credentials, identity claims, or real user data. Keep `.streamlit/secrets.toml` and `.env` untracked.
- Do not migrate, delete, rewrite, or assign ownership to existing JSON/Supabase data unless the Sprint explicitly defines mapping, snapshot, validation, and rollback.
- Persist only approved minimum identity data. Raw OIDC claims are not storage keys.
- Treat Supabase secret/service-role keys as server-only RLS-bypass credentials; every user-data query must enforce trusted ownership in server code.
- Do not add paid API calls without explicit approval.

## Efficient implementation

- Make one coherent behavior change at a time and keep unrelated user changes untouched.
- Run the smallest relevant tests while implementing. Run the full suite once after the last code change; repeat it only if code changes afterward.
- Run compilation and one local Streamlit smoke test before deployment.
- Prefer small, reviewable commits: behavior and its tests together; schema/storage changes separately when independently reversible; documentation separately.
- Do not mark a Sprint complete before the final commit is pushed and the deployed anonymous read path is verified.

## Documentation contract

Update a document only when its role changed, and link instead of repeating detail.

- `README.md`: setup, secrets, local run, tests, deployment, and operation only.
- `ROADMAP.md`: ordered outcomes and status only; no implementation narrative.
- `CHANGELOG.md`: release-relevant user, security, or operational changes only.
- `docs/PROJECT_CONTEXT.md`: durable product invariants and architecture decisions only.
- `docs/sprints/NN-*.md`: the Sprint's scope, threat/risk decisions, implementation summary, verification, deployment result, and next boundary.
- `docs/sprints/README.md`: archive index and Sprint-record template only.
- `BRAND.md` and `PRINCIPLES.md`: product narrative and principles; do not duplicate them in README.

## Completion sequence

1. Confirm targeted tests, then run `python -m unittest discover -v` once.
2. Compile Python, run a local Streamlit health/root smoke test, run `git diff --check`, scan for secrets, and confirm protected data files are unchanged.
3. Update only applicable documents and leave the Sprint status as deployment pending.
4. Commit, push `main`, and verify the deployed Streamlit anonymous home/read path and protected management boundary.
5. Record the deployed commit and verification result, set the Sprint to complete, commit and push that concise record.
6. Report changes, tests, commits, deployment, user actions, and the next Sprint candidate.
