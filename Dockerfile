# One container for Cloud Run: Next.js standalone server on $PORT, FastAPI on 127.0.0.1:8000 behind it.
# Secrets (GEMINI_API_KEY) are provided at runtime by Cloud Run; nothing secret is copied into the image.

FROM node:22-bookworm-slim AS frontend
WORKDIR /src
ENV NEXT_TELEMETRY_DISABLED=1
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm
COPY --from=node:22-bookworm-slim /usr/local/bin/node /usr/local/bin/node
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production \
    PORT=8080
WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt
COPY backend/app backend/app

COPY --from=frontend /src/.next/standalone frontend/
COPY --from=frontend /src/.next/static frontend/.next/static
COPY --from=frontend /src/public frontend/public
COPY start.sh ./

RUN useradd --create-home --uid 1001 app \
 && mkdir -p backend/data \
 && chown -R app:app backend/data
USER app

EXPOSE 8080
CMD ["./start.sh"]
