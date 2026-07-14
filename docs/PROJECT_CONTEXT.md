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

## Data and authorization model

- Anonymous visitors may read news and use the existing growth-record flow.
- Logged-in users not listed in `ADMIN_EMAILS` are read-only.
- Only allowlisted administrators may mutate news or global interests/goals.
- Protected writes are checked at both page and service boundaries.
- Current interests, goals, growth, and analytics records remain the legacy global/anonymous dataset.
- Empty owner-scoped Supabase tables and server-only access primitives are defined separately from legacy tables. Direct `anon` and `authenticated` table access is denied; the server must constrain every operation by opaque `owner_id`.
- User-data routing and legacy-data migration are not active. Existing rows must not be assigned to an owner without an explicit mapping, snapshot, validation, and rollback plan.
- A server-privileged Supabase key is a backend credential; public UI must never provide an unrestricted indirect write path.

## Documentation map

- `AGENTS.md`: short execution rules automatically discovered by Codex.
- `.codex/config.toml`: trusted-project Codex defaults, including high reasoning effort.
- `README.md`: concise product introduction, setup, authentication configuration, and operation.
- `ROADMAP.md`: ordered future outcomes.
- `CHANGELOG.md`: user-visible changes.
- `docs/sprints/`: one decision and verification record per Sprint.

## Near-term direction

After Sprint 07, activate user-scoped storage in a separate Sprint: deploy and verify the empty schema, configure server-only secrets, test two-user isolation, then switch authenticated personal-data flows without auto-assigning legacy rows. Keep the anonymous legacy path until a separately approved migration proves ownership and rollback.
