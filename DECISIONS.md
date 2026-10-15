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

## 2026-10-15 — Seed data: what goes in the DB vs. stays on disk
**Context:** Step 1 asks for a seed loader and `POST /admin/reset`, but the full data model arrives in Step 2.
**Decision:** Reset drops and recreates every table and loads only reference data (`Institution`, defined now in `app/models.py`). The SMS export, mailbox, AIS, DigiLocker and registry files stay in `backend/seed/` as mock external sources, read from disk when the heir connects them. Reset also checks all seed files exist and parse. The app resets on every startup. `/admin/reset` is unauthenticated.
**Why:** Simplest thing that matches "re-seeded on startup / via reset endpoint". The data is synthetic, so an open reset on the demo can only reset the demo.

## 2026-10-15 — Seed data: two extra institutions and two extra files
**Context:** The brief lists six institutions, but the physical share certificate needs an issuer, and the console needs the insurer's own view of the policy.
**Decision:** Added Bharat Textile Mills (fictional, issuer of the 1994 certificate; a different company from the hidden-shares one, so the scan is its own asset) → 7 institutions, 7 expected assets. Added `lic_policy_record.json` (nominee = Ananya) and `expected_assets.json` (answer key for tests). Companies are fictional; banks/insurer/RTA use real names as labels only.
**Why:** Gives the "≈7 assets incl. 1 suggested" target from BUILD_PROMPTS.md without the scan accidentally confirming the inferred shares.

## 2026-10-15 — Seed data: confidence and status conventions
**Context:** AGENTS.md defines confidence (High/Medium/Suggested) and status (suggested/confirmed/rejected) but not where some sources fall, or what status a found asset starts in.
**Decision:** A CAMS CAS counts as an official statement (High on its own). A single registry hit (UDGAM) and a single scan are one direct source (Medium). LIC premium emails are one direct source (Medium). Every discovered asset starts with status `suggested`; only the heir's "Yes" sets `confirmed` (rule 7). Value bands: Under ₹1 lakh, ₹1–5 lakh, ₹5–15 lakh, ₹15–50 lakh, Over ₹50 lakh.
**Why:** Keeps "humans confirm" literal and gives tests one unambiguous answer per asset.

## 2026-10-15 — Synthetic document images are visibly marked
**Context:** The death certificates and share certificate are generated images.
**Decision:** Every generated image has a red "DEMO · SYNTHETIC DATA · NOT A REAL DOCUMENT" band and a diagonal watermark, and names a "demo registry". Generated deterministically by `seed/generate_images.py`; the PNGs are committed. Pillow is a dev dependency only.
**Why:** AGENTS.md rule 6; the images must never pass as real documents if they leave the demo.
