PRIVACY_POLICY_VERSION = "1.0"

PRIVACY_POLICY_SUMMARY = """
This system exists to help students document and report cyber harassment safely.

- You can file a report anonymously; your identity is hidden from everyone
  except the counselor/legal staff assigned to your case (never from the public).
- Uploaded evidence is encrypted at rest (AES-256) and integrity-checked (SHA-256)
  so no one - including system administrators - can quietly alter it.
- Access to your case is logged in a tamper-evident audit trail.
- Your data is retained only as long as needed for your case and applicable
  legal requirements, and is never sold or shared with third parties.
- You may request a copy of your data or ask that non-essential data be deleted,
  subject to legal hold requirements on active cases.
""".strip()


def get_policy() -> dict:
    return {"version": PRIVACY_POLICY_VERSION, "summary": PRIVACY_POLICY_SUMMARY}
