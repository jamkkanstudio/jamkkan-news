# Jamkkan working agreement

Read `docs/PROJECT_CONTEXT.md` before changing the product. Use `ROADMAP.md` for priorities and the latest file in `docs/sprints/` for the current baseline.

## Non-negotiable rules

- Keep public reading and growth-record flows working without login or secrets.
- Require the deployment `ADMIN_EMAILS` allowlist for every global content or setting write, including service-level entry points.
- Never commit or print OAuth, Supabase, GitHub, or AI credentials. Keep `.streamlit/secrets.toml` and `.env` untracked.
- Do not migrate, delete, or rewrite existing JSON/Supabase data unless a Sprint explicitly authorizes it.
- Do not store identity claims before user data isolation is designed and approved.
- Do not add paid API calls without explicit approval.
- Use small commits, run all tests, push `main`, and verify the deployed Streamlit read path for every completed Sprint.
- Start each new Sprint in a new Codex task.
- At the start of each Sprint, rename its Codex task to `Sprint NN — concise goal`.

## Definition of done

Update tests, `CHANGELOG.md`, `ROADMAP.md`, and one concise Sprint record. Keep `README.md` limited to setup and operation. Record durable product or architecture decisions only in `docs/PROJECT_CONTEXT.md`.
