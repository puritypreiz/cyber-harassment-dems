# Security Policy

## Reporting a vulnerability

If you discover a security vulnerability in this system, report it privately
to the system administrators rather than filing a public issue. Include
reproduction steps and impact. Do not test against production data or other
users' accounts without authorization.

## Controls implemented

- **Authentication**: bcrypt password hashing (cost factor 12), JWT access
  (short-lived) + refresh tokens, optional TOTP-based MFA, account lockout
  after 5 failed attempts (15-minute cooldown).
- **Authorization**: role-based access control (student/counselor/legal/admin)
  enforced at the route level, plus object-level checks so, e.g., a counselor
  can only act on cases assigned to them.
- **Evidence encryption**: AES-256-GCM at rest; the key is never stored
  alongside the ciphertext. SHA-256 integrity hashing detects any
  post-upload tampering or corruption.
- **Chain of custody**: every security-relevant action is recorded in a
  hash-chained, RSA-signed audit log. Signed QR codes let evidence integrity
  be verified independently of the system's own UI.
- **Input validation**: server-side validation on every API boundary; file
  uploads are validated by both extension and sniffed content type (not
  filename alone), with a hard size cap.
- **Transport/session security**: strict security headers (CSP, X-Frame-Options,
  HSTS, nosniff), CSRF protection on cookie-based flows, rate limiting on
  authentication and upload endpoints, `Cache-Control: no-store` to avoid
  caching sensitive responses.
- **Least privilege on storage**: uploaded files are written with `0600`
  permissions; filenames are never derived from user input (avoids path
  traversal).

## Known limitations / operator responsibilities

- The in-memory rate limiter and token-revocation list do not survive process
  restarts and aren't shared across multiple app instances — see
  `docs/DEPLOYMENT_GUIDE.md` for the Redis-backed alternative at scale.
- This system does not itself provide network-layer protections (WAF, DDoS
  mitigation) — deploy behind an appropriately configured reverse proxy/CDN.
- Regularly rotate `JWT_SECRET_KEY` and review `/api/admin/audit-log` for
  anomalous activity.
