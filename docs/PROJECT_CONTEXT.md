# Jamkkan project context

This is the minimum durable context needed to continue Jamkkan from GitHub with a new developer or Codex account. Update it only when a product invariant or architecture decision changes.

## Product direction

Jamkkan turns very short idle moments into sustainable growth. The news product is the first implementation: a small daily briefing, personalized ranking, and a visible growth record without infinite-scroll or attention-capture mechanics. Future content areas may include books, movies, fitness, finance, and learning.

## Current architecture

- Streamlit multipage UI in `app.py`, `pages/`, and `components/`.
- Domain logic in `services/`; tests use standard-library `unittest`.
- Existing JSON files remain the operational baseline. Supabase mirrors news, interests, settings, and growth data.
- Daily and weekly behavior uses `Asia/Seoul`.
- Streamlit native OIDC provides Google login. Email is used in memory for the administrator allowlist only.
- User ownership is derived on demand from the OIDC `(issuer, subject)` pair with a server-only HMAC pepper. Only the resulting opaque owner id may be persisted; raw identity claims are not user-data keys.
- A default-off `USER_DATA_ENABLED` compatibility layer switches authenticated interests, goals, growth, and analytics together; partial routing is not allowed. Production routing was enabled only after the empty schema, role boundaries, and two-account isolation passed verification.

## Data and authorization model

- Anonymous visitors may read news and use the existing growth-record flow.
- Logged-in users not listed in `ADMIN_EMAILS` are read-only.
- Only allowlisted administrators may mutate news or global interests/goals.
- Protected writes are checked at both page and service boundaries.
- With user-data routing disabled, current interests, goals, growth, and analytics records remain the legacy global/anonymous dataset.
- Empty owner-scoped Supabase tables and server-only access primitives are defined separately from legacy tables. Direct `anon` and `authenticated` table access is denied; the server must constrain every operation by opaque `owner_id`.
- Authenticated user-data routing is enabled in production after protected legacy snapshots, an empty-schema rollout, server-only secret configuration, and two-account isolation verification. Existing rows remain unmapped and must not be assigned to an owner without an explicit mapping, snapshot, validation, and rollback plan.
- A server-privileged Supabase key is a backend credential; public UI must never provide an unrestricted indirect write path.

## Documentation map

- `AGENTS.md`: short execution rules automatically discovered by Codex.
- `.codex/config.toml`: trusted-project Codex defaults, including high reasoning effort.
- `README.md`: concise product introduction, setup, authentication configuration, and operation.
- `ROADMAP.md`: ordered future outcomes.
- `CHANGELOG.md`: user-visible changes.
- `docs/sprints/`: one decision and verification record per Sprint.

## Near-term direction

Keep the activated personal-data path monitored while preserving the anonymous legacy path and all existing rows. The next operational outcome is an automatic news-collection pipeline with duplicate protection and failure visibility; any future legacy ownership migration still requires separately approved mapping and rollback.
