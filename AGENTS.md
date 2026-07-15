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

## Credit-efficient checkpoints

- After the read-only audit, name the affected test modules once. Run them in one consolidated command after the last related behavior change; do not rerun unchanged targeted tests for each small edit.
- Treat the successful full suite as valid after documentation-only edits and conflict-free rebases of data-only collection commits. Rerun it only when executable code or test code changes.
- Combine final compilation, configuration parsing, `git diff --check`, credential-pattern scanning, and protected-data comparison into one verification pass. Reuse that evidence in the Sprint record instead of collecting it again.
- Use one known local Streamlit smoke method. If startup fails, inspect process/port output once before retrying rather than trying multiple launch variants.
- Use one browser session after push to verify the anonymous home/read path, the changed interaction, the management boundary, and console errors. Avoid repeated screenshots or full DOM reads when a targeted count or state proves the result.
- Fetch at Sprint start and once immediately before push. If the second fetch adds only reviewed automatic data commits and rebase is conflict-free, preserve them without repeating code verification.
- Do not reread unchanged baseline documents, repeat broad searches, or recompute evidence already captured in the current Sprint unless new scope or a conflicting change makes it stale.

## Documentation contract

Update a document only when its role changed, and link instead of repeating detail.

- `README.md`: a concise user-facing brand introduction followed by setup, secrets, local run, tests, deployment, and operation. Link to `BRAND.md` and `PRINCIPLES.md` instead of duplicating their full narrative.
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
