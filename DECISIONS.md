# Decisions

Choices made where AGENTS.md or BUILD_PROMPTS.md left room. Newest at the bottom.

Template:

```
## YYYY-MM-DD — Short title
**Context:** what was ambiguous.
**Decision:** what we chose.
**Why:** one or two lines.
```

---

## 2026-10-15 — App name placeholder
**Context:** AGENTS.md says to use `{{reclaim}}` everywhere; Step 0 in BUILD_PROMPTS.md says `{{APP_NAME}}`.
**Decision:** Use `{{reclaim}}`, defined once in `frontend/lib/app.ts`.
**Why:** AGENTS.md is the project brief and says to use that string everywhere. One constant keeps the later rename to a one-line change.

## 2026-10-15 — One container: Next.js standalone + uvicorn, started by a shell script
**Context:** Cloud Run needs one port; we have a Next.js frontend and a FastAPI backend.
**Decision:** Build Next.js with `output: "standalone"`. In the container, `start.sh` starts uvicorn on `127.0.0.1:8000`, waits for `/health`, then starts `node server.js` on `$PORT`. A Next.js rewrite proxies `/api/*` to FastAPI (prefix stripped, so `/api/health` → `/health`). If either process exits, the container exits and Cloud Run restarts it. No nginx, no supervisord.
**Why:** Fewest moving parts. The browser only talks to one origin, so there's no CORS, and the same rewrite works in local dev.

## 2026-10-15 — GEMINI_API_KEY via Secret Manager on Cloud Run
**Context:** The key must come from the environment at runtime and never be baked into the image.
**Decision:** `cloudbuild.yaml` deploys with `--set-secrets=GEMINI_API_KEY=gemini-api-key:latest`, so Cloud Run injects it as an env var. `.env` is in `.dockerignore`. The backend reads the key when it creates a client (`backend/app/llm.py`).
**Why:** Keeps the key out of the image, the build logs and the repo.

## 2026-10-15 — Single Cloud Run instance
**Context:** v0 storage is SQLite inside the container.
**Decision:** Deploy with `--max-instances=1`.
**Why:** Several instances would each have their own database and the demo would look inconsistent. Revisit if we move to Cloud SQL.

## 2026-10-15 — Default Gemini model
**Context:** `gemini-2.5-flash` returns 404 for new keys.
**Decision:** Default to `gemini-3.8-flash` (listed as available for our key), overridable with `GEMINI_MODEL`.
**Why:** Newest generally available Flash model the key can use.
