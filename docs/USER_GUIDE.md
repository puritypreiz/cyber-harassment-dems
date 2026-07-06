# User Guide

## For students

1. **Register** at `/register` with a username, email, and a strong password.
   You can optionally enable multi-factor authentication afterward from your
   account settings.
2. **File a case** from your dashboard (`/dashboard`). Describe what happened;
   the system suggests a category and severity, and automatically assigns the
   least-loaded available counselor. You may file anonymously — your identity
   is then hidden from anyone without a legitimate need to see it.
3. **Upload evidence** (screenshots, message exports, recordings) from the
   case's "Manage evidence" page. Files are encrypted immediately and hashed
   with SHA-256; a QR code is generated for each item.
4. **Track your case** — status updates trigger an email notification, and you
   can view the full chain-of-custody timeline for your case.
5. **Crisis resources** are always visible on the home page and dashboard,
   including a national hotline and category-specific resources (e.g.
   image-removal services for non-consensual imagery cases).

## For counselors

Log in and you're routed to `/counselor`, showing cases assigned to you. You
can update case status (open → under review → escalated → resolved/closed);
the reporting student is notified automatically.

## For legal staff

`/legal` lists your assigned cases. Each case has an "Export chain-of-custody
report" action, producing a signed PDF (plus JSON) suitable for use in legal
proceedings — it embeds every evidence hash, the full audit trail, and the
system's public signing key for independent verification.

## For admins

`/admin` provides user management, an audit-log viewer with one-click
signature/chain verification, and a list of closed cases due for data-retention
review (purges are never automatic — a human always signs off).

## Verifying evidence with a QR code

Every evidence item's QR code encodes a signed token proving its SHA-256 hash
at the time of upload. From the evidence detail page you can scan a QR code
(using your device camera, where supported) or paste the token text; the
system checks (a) the signature is genuine and (b) the file's current hash
still matches — flagging any tampering since upload.
