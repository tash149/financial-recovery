# {{reclaim}}

Helps an heir find and claim the financial assets of a parent who has died, and helps an insurer verify death claims. v0 is a demo on **synthetic data only**. Project brief: [AGENTS.md](AGENTS.md). Build steps: [BUILD_PROMPTS.md](BUILD_PROMPTS.md). Choices made along the way: [DECISIONS.md](DECISIONS.md).

## Layout

| Path | What |
|---|---|
| `backend/` | FastAPI + SQLModel (SQLite), pytest. Python 3.11. |
| `backend/seed/` | Synthetic demo data + answer key ([README](backend/seed/README.md)). `POST /admin/reset` reloads it. |
| `frontend/` | Next.js (App Router, TypeScript, Tailwind). Node 22. |
| `Dockerfile`, `start.sh` | One container for Cloud Run (frontend + backend). |
| `cloudbuild.yaml` | Build and deploy to Cloud Run (`heir-app`, `asia-south1`). |

## Run locally

Needs Python 3.11 and Node 22.

```bash
cp .env.example .env   # then add your GEMINI_API_KEY
./dev.sh
```

`dev.sh` installs dependencies on first run, then starts both apps:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health (also reachable through the frontend at http://localhost:3000/api/health)

Ctrl+C stops both.

### Tests

```bash
cd backend && .venv/bin/pytest
```

### Check the Gemini key

```bash
cd backend && set -a && . ../.env && set +a && .venv/bin/python -m scripts.gemini_smoke
```

Prints the key's length (never the key) and a one-word reply from the model.

## Run the container locally

```bash
docker build -t heir-app .
docker run --rm -p 8080:8080 -e GEMINI_API_KEY heir-app
```

Open http://localhost:8080. The key is passed at runtime and is never part of the image.

## Deploy to Cloud Run

One-time setup in your Google Cloud project:

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create heir-app --repository-format=docker --location=asia-south1
printf %s "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
# Let Cloud Run's runtime service account read the secret:
PROJECT_NUMBER=$(gcloud projects describe "$(gcloud config get-value project)" --format='value(projectNumber)')
gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role=roles/secretmanager.secretAccessor
```

The Cloud Build service account also needs permission to deploy to Cloud Run (`roles/run.admin` and `roles/iam.serviceAccountUser`).

Then build and deploy:

```bash
gcloud builds submit --config cloudbuild.yaml
```
