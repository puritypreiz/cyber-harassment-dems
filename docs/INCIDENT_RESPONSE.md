# Incident Response Plan

## Scope

This plan covers security incidents affecting the DEMS platform itself
(breach, data exposure, integrity compromise) — not individual harassment
cases, which are handled via the normal case-management workflow.

## Severity triage

| Level | Examples | Initial response time |
|---|---|---|
| Critical | Evidence encryption key or signing key compromised; unauthorized admin access; mass data exposure | Immediate |
| High | Single-account compromise; audit-log integrity check fails | Within 4 hours |
| Medium | Suspicious repeated failed logins; rate-limit abuse | Within 24 hours |
| Low | Isolated validation/error-handling bug with no data exposure | Next business day |

## Response steps

1. **Contain**: disable the affected account(s) via
   `POST /api/admin/users/<id>/deactivate`; if infrastructure is compromised,
   rotate `SECRET_KEY`/`JWT_SECRET_KEY` immediately (this invalidates all
   sessions) and take the affected instance offline if needed.
2. **Assess**: run `GET /api/admin/audit-log/verify` to confirm whether the
   chain-of-custody log itself has been tampered with. Review
   `logs/security.log` and `logs/audit.log` for the incident window.
3. **Eradicate**: patch the root cause; if a secret was exposed, rotate it
   (see `docs/DEPLOYMENT_GUIDE.md` for which secrets require what follow-up).
4. **Recover**: restore from `storage/backups/` if data integrity was
   affected; re-verify evidence hashes for any affected cases via
   `POST /api/cases/<id>/evidence/<id>/verify`.
5. **Notify**: affected students must be notified promptly and clearly,
   consistent with applicable breach-notification law and the institution's
   Title IX/legal obligations — loop in legal staff immediately for any
   incident involving student data.
6. **Post-mortem**: document root cause, timeline, and remediation; update
   this plan and `docs/SECURITY_POLICY.md` if gaps are found.

## Key contacts

Fill in for your deployment: security lead, legal/Title IX office, hosting
provider abuse contact, and the institution's incident response team.
