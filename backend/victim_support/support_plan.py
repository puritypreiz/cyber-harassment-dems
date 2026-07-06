from backend.utils.constants import SeverityLevel

_BASE_STEPS = [
    "Preserve original copies of any messages, images, or posts before blocking or deleting accounts.",
    "Review and tighten privacy settings on affected social media accounts.",
    "Avoid direct confrontation with the harasser; let case staff coordinate a response.",
]

_SEVERITY_STEPS = {
    SeverityLevel.CRITICAL: [
        "A counselor will reach out within 24 hours - if you feel unsafe right now, contact campus security or emergency services immediately.",
        "Legal staff will be looped in to assess options including a protective order.",
    ],
    SeverityLevel.HIGH: [
        "A counselor will reach out within 48 hours to discuss next steps and support options.",
    ],
    SeverityLevel.MEDIUM: [
        "A counselor will review your case within 3-5 business days.",
    ],
    SeverityLevel.LOW: [
        "Your case has been logged; a staff member will review it during regular case triage.",
    ],
}


def build_support_plan(case) -> dict:
    return {
        "case_id": case.id,
        "severity": case.severity,
        "steps": [*_SEVERITY_STEPS.get(case.severity, []), *_BASE_STEPS],
    }
