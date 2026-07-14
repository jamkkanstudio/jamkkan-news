# Jamkkan project context

This is the minimum durable context needed to continue Jamkkan from GitHub with a new developer or Codex account. Update it only when a product invariant or architecture decision changes.

## Product direction

Jamkkan turns very short idle moments into sustainable growth. The news product is the first implementation: a small daily briefing, personalized ranking, and a visible growth record without infinite-scroll or attention-capture mechanics. Future content areas may include books, movies, fitness, finance, and learning.

## Current architecture

- Streamlit multipage UI in `app.py`, `pages/`, and `components/`.
- Domain logic in `services/`; tests use standard-library `unittest`.
- Existing JSON files remain the operational baseline. Supabase mirrors news, interests, settings, and growth data.
- Daily and weekly behavior uses `Asia/Seoul`.
- Streamlit native OIDC provides Google login. Identity claims are used only for display and authorization in this phase.

## Data and authorization model

- Anonymous visitors may read news and use the existing growth-record flow.
- Logged-in users not listed in `ADMIN_EMAILS` are read-only.
- Only allowlisted administrators may mutate news or global interests/goals.
- Protected writes are checked at both page and service boundaries.
- Current interests and goals are global, not per-user. User-specific isolation and migration are deferred to a dedicated Sprint.
- A server-privileged Supabase key is a backend credential; public UI must never provide an unrestricted indirect write path.

## Documentation map

- `AGENTS.md`: short execution rules automatically discovered by Codex.
- `.codex/config.toml`: trusted-project Codex defaults, including high reasoning effort.
- `README.md`: setup, authentication configuration, and operation.
- `ROADMAP.md`: ordered future outcomes.
- `CHANGELOG.md`: user-visible changes.
- `docs/sprints/`: one decision and verification record per Sprint.

## Development loop

1. Confirm clean `main`; read this file and the latest Sprint record.
2. State the Sprint scope and preserve existing data.
3. Implement reviewable units with tests.
4. Run `python -m unittest discover -v` and a local Streamlit smoke test.
5. Update only the relevant document roles above.
6. Commit, push `origin/main`, and verify the deployed anonymous read path.
7. Report deployment-only secret names and locations, never their values.

## Near-term direction

After Sprint 06, the next major security boundary is deliberate user-data isolation. Plan it as a new Sprint before persisting identity claims or migrating global data.
