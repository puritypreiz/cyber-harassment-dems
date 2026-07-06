# API Documentation

All endpoints are JSON over HTTPS. Authenticate with `Authorization: Bearer
<access_token>` (obtained from `/api/auth/login`). Endpoints marked **(role)**
require that role (or admin, which can access everything).

## Auth (`/api/auth`)

| Method | Path | Description |
|---|---|---|
| POST | `/register` | Create a student account. |
| POST | `/login` | Returns `access_token` + `refresh_token`. Returns `401` with `mfa_required: true` if MFA is enabled and no `totp_code` was supplied. |
| POST | `/refresh` | Exchange a refresh token for a new access token. |
| POST | `/logout` | Revokes the current access token (and refresh token, if supplied). |
| POST | `/mfa/setup` | Generates a TOTP secret + provisioning QR (SVG). |
| POST | `/mfa/enable` | Confirms a TOTP code to turn MFA on. |
| POST | `/mfa/disable` | Turns MFA off. |
| GET | `/me` | Current user profile. |

## Cases (`/api/cases`)

| Method | Path | Description |
|---|---|---|
| POST | `` | Create a case. Category/severity are auto-suggested if not provided; a counselor is auto-assigned. |
| GET | `` | List cases visible to the caller (own cases for students; assigned cases for staff; all for admin). |
| GET | `/<case_id>` | Case detail. |
| PATCH | `/<case_id>/status` | Update status. **(counselor/legal assigned to the case, or admin)** |
| POST | `/<case_id>/assign-counselor` | **(admin/counselor)** |
| POST | `/<case_id>/assign-legal` | **(admin/legal)** |
| GET | `/<case_id>/timeline` | Chain-of-custody timeline for the case. |
| GET | `/<case_id>/support-plan` | Suggested support-plan steps. |

## Evidence (`/api/cases/<case_id>/evidence`)

| Method | Path | Description |
|---|---|---|
| POST | `` | Multipart upload (`file`, optional `description`). Validated, encrypted (AES-256-GCM), hashed (SHA-256), and a signed QR code is generated. |
| GET | `` | List evidence for the case. |
| GET | `/<evidence_id>` | Evidence metadata. |
| GET | `/<evidence_id>/download` | Decrypts and streams the original file. |
| POST | `/<evidence_id>/verify` | Re-decrypts and re-hashes the stored file to confirm it still matches the hash recorded at upload time. |

## QR (`/api/qr`)

| Method | Path | Description |
|---|---|---|
| GET | `/evidence/<evidence_id>/image` | PNG of the evidence's QR code. |
| POST | `/verify` | Body: `{"token": "..."}`. Verifies the QR's signature and whether the referenced evidence's current hash still matches. |

## Reports (`/api/cases/<case_id>/report`)

| Method | Path | Description |
|---|---|---|
| GET | `` | **(admin/legal/counselor)** Generates and downloads a signed chain-of-custody PDF (with an accompanying JSON alongside it in storage). |

## Admin (`/api/admin`) — all admin-only unless noted

| Method | Path | Description |
|---|---|---|
| GET | `/users` | List users. |
| PATCH | `/users/<user_id>/role` | Change a user's role. |
| POST | `/users/<user_id>/deactivate` | Deactivate an account. |
| GET | `/audit-log` | **(admin/legal)** Paginated audit trail. |
| GET | `/audit-log/verify` | **(admin/legal)** Verifies every entry's signature and hash-chain linkage. |
| GET | `/signing-public-key` | RSA public key used to sign audit entries (any authenticated user). |
| GET | `/retention/review-candidates` | **(admin/legal)** Closed cases past the retention window. |

## Public/support (`/api`)

| Method | Path | Description |
|---|---|---|
| GET | `/privacy-policy` | Current privacy policy text/version. |
| GET | `/support/hotline` | Crisis hotline numbers. |
| GET | `/support/resources` | Resource list, optionally filtered by `?category=`. |
| POST/GET/DELETE | `/consent/<consent_type>` | Grant/check/revoke a consent record (authenticated). |

## Error format

Errors are `{"error": "message"}` or `{"errors": {"field": "message"}}` for
validation failures, with an appropriate HTTP status code (`400`, `401`,
`403`, `404`, `409`, `423`, `429`).
