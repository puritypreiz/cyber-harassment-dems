# Legal & Compliance Notes

This document is informational, not legal advice — have counsel review your
specific deployment against applicable law (this varies significantly by
jurisdiction and institution type).

## Evidentiary integrity

The chain-of-custody design (AES-256 encryption, SHA-256 hashing, RSA-signed
hash-chained audit log, signed QR codes) is intended to support the kind of
integrity showing often required for evidence to be admissible — i.e.
demonstrating that a record has not been altered since capture and who
accessed it when. `GET /api/cases/<id>/report` produces a report bundling
this information along with the system's public signing key for independent
verification. This is a technical aid, not a substitute for your
institution's own evidentiary procedures.

## Student privacy

- **Title IX (US institutions)**: cyber harassment/sexual harassment reports
  involving students may trigger Title IX obligations. Legal/Title IX staff
  should be looped in via case assignment (`assign-legal`) for any case that
  may qualify, and institutions should ensure this system's workflows align
  with their Title IX grievance procedures rather than replace them.
- **FERPA (US)**: case and evidence records containing student education
  records should be treated as protected; access is already restricted to
  the reporter and assigned staff (see `backend/security/access_control.py`),
  but institutions must apply their own FERPA disclosure procedures for any
  export or law-enforcement request.
- **Anonymity**: a student may file anonymously (`is_anonymous`); their
  identity is withheld from anyone without a legitimate operational need,
  including in exported reports where feasible (`backend/privacy/anonymizer.py`).

## Data retention

`backend/privacy/data_retention.py` surfaces closed cases past the configured
retention window (`DATA_RETENTION_DAYS_DEFAULT`, default ~5 years) for human
review — nothing is purged automatically. Any case under legal hold or active
proceedings should be explicitly retained regardless of age; document that
decision via `mark_reviewed_for_retention`.

## Consent

`backend/privacy/consent_manager.py` tracks consent for data processing,
evidence sharing, and counselor referral separately, so a student's consent
for one purpose (e.g. counseling support) doesn't imply consent for another
(e.g. sharing evidence with a third party).
