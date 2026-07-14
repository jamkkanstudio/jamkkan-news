# Sprint 06 — Google login and admin protection

## Goal

Add Streamlit native Google OIDC while keeping public reading available when authentication is absent, and close all global news/settings write paths to non-admin users.

## Decisions

- Use `st.login`, `st.user`, and `st.logout` with Authlib 1.3.2 or newer.
- Read administrator identities only from deployment secret `ADMIN_EMAILS`.
- Check authorization at both protected pages and mutation service functions.
- Keep growth recording public and preserve every existing JSON/Supabase row.
- Do not persist OIDC identity claims in this Sprint.
- Use HTTPS for configured RSS feeds and show generic collection failures.

## Protected operations

- News add, update, and delete.
- RSS collection and registration.
- Global interests and daily-goal changes.

## Verification

Automated coverage includes missing configuration, anonymous identity, logged-in non-admin, allowlisted admin, login/logout UI calls, and service-boundary denial.

- `python -m unittest discover -v`: 34 passed.
- Python compilation: passed.
- Local Streamlit health endpoint without auth secrets: HTTP 200 `ok`.
- Existing `data/` files: unchanged.
- Deployed anonymous read path: recorded after the documentation commit is pushed.

## Deployment-only setup

The repository contains no OAuth values. The owner configures Streamlit app secrets using `README.md` and adds the exact deployed callback URI to the Google OAuth web client. Local development uses an untracked `.streamlit/secrets.toml` and localhost callback URI.
