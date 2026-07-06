# Deployment Guide

## Prerequisites

- Python 3.11+, or Docker + Docker Compose.
- `libmagic` (system package) for content-based file-type detection —
  `apt-get install libmagic1` on Debian/Ubuntu, already included in the
  provided `Dockerfile`.
- A Postgres database for production (SQLite is fine for development/small
  deployments only — it does not handle concurrent writes well).

## Required secrets (`.env`)

Generate each of these with
`python3 -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())"`
and never commit them:

- `SECRET_KEY` — Flask session/signing key.
- `JWT_SECRET_KEY` — separate key for JWT signing (rotating this invalidates
  all outstanding tokens).
- `EVIDENCE_ENCRYPTION_KEY` — AES-256 key for evidence at rest. **Losing this
  key makes all previously uploaded evidence unrecoverable.** Back it up
  securely (e.g. a secrets manager), separately from the database.
- `QR_SIGNING_KEY` — HMAC key for QR token signatures.

The RSA keypair used to sign chain-of-custody audit entries is generated
automatically on first run and stored under `storage/keys/` — back this up
too, or historical audit entries won't be re-verifiable after a key loss
(though existing entries stay readable; only new signing requires the key).

## Steps

1. `cp .env.example .env` and fill in the secrets above plus `DATABASE_URL`
   and (if using the provided `docker-compose.yml`) `POSTGRES_PASSWORD`.
2. `docker compose up --build -d`
3. The app is served by Gunicorn on port 8000 — put a reverse proxy (nginx,
   Caddy, or a cloud load balancer) in front of it for TLS termination.
   `SESSION_COOKIE_SECURE` is on by default outside `FLASK_ENV=development`,
   so the app must be served over HTTPS in production.
4. Set `ALLOWED_ORIGINS` if the frontend is served from a different origin
   than the API (leave blank if it's all one origin, which is the default
   setup here).
5. Back up `storage/` (encrypted evidence, QR codes, signing keys) and the
   database on a regular schedule — see `storage/backups/` as the convention
   for where backup archives should land.

## Scaling notes

- The in-memory rate limiter and revoked-token store
  (`backend/security/rate_limiter.py`, `backend/security/session_manager.py`)
  are per-process. For a multi-instance deployment, back both with Redis
  (`RATE_LIMIT_STORAGE_URI=redis://...` and a small code change to
  `session_manager.py`) so limits/revocations are shared.
- `backend/database/database.py` uses `db.create_all()` for first-run schema
  setup. For subsequent schema changes, use Flask-Migrate
  (`flask db migrate`, `flask db upgrade`) rather than editing the running
  database by hand.
