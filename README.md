# Cyber Harassment Digital Evidence Management System (DEMS)

A secure, survivor-centered platform for students to document, report, and track
cyber harassment cases. Evidence is encrypted at rest, integrity-checked with
SHA-256, and paired with a signed QR code for chain-of-custody verification.

## Key features

- **Encrypted evidence storage** — AES-256-GCM encryption at rest, SHA-256
  integrity hashing, and file-type/content validation on upload.
- **QR-verified chain of custody** — every evidence item gets a signed QR code;
  scanning it (or pasting the token) cryptographically proves the file hasn't
  been altered since upload.
- **Tamper-evident audit trail** — every security-relevant action is recorded in
  a hash-chained, RSA-signed audit log (`backend/chain_of_custody`).
- **RBAC** — student / counselor / legal / admin roles, enforced at both the
  route level (`backend/auth/roles.py`) and the object level
  (`backend/security/access_control.py`).
- **MFA** — optional TOTP-based multi-factor authentication.
- **Survivor-centered workflows** — anonymous reporting, automatic
  least-loaded-counselor assignment, keyword-assisted triage/severity scoring,
  and built-in crisis resources.
- **Privacy tooling** — consent tracking, EXIF/GPS stripping on exports, and a
  human-in-the-loop data-retention review process.

## Quick start (local development)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# Generate the required secrets and paste them into .env:
python3 -c "import base64,os;print(base64.b64encode(os.urandom(32)).decode())"

python -m backend.database.seed   # optional demo accounts (see output for password)
python app.py                     # http://127.0.0.1:5000
```

Run the test suite:

```bash
pytest tests/ -q
```

## Architecture

See the top-level directory layout for the module breakdown: `backend/auth`,
`backend/evidence`, `backend/harassment`, `backend/chain_of_custody`,
`backend/victim_support`, `backend/privacy`, `backend/security`,
`backend/database`, and `backend/api` (Flask blueprints). `frontend/templates`
and `frontend/static` hold the server-rendered UI.

Further documentation lives in `docs/`:

- [`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md)
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md)
- [`docs/DEPLOYMENT_GUIDE.md`](docs/DEPLOYMENT_GUIDE.md)
- [`docs/SECURITY_POLICY.md`](docs/SECURITY_POLICY.md)
- [`docs/INCIDENT_RESPONSE.md`](docs/INCIDENT_RESPONSE.md)
- [`docs/LEGAL_COMPLIANCE.md`](docs/LEGAL_COMPLIANCE.md)

## Running with Docker

```bash
cp .env.example .env   # fill in secrets; set POSTGRES_PASSWORD too
docker compose up --build
```

This starts the app behind Gunicorn with a Postgres database. Evidence,
QR codes, reports, and logs persist in named Docker volumes.
