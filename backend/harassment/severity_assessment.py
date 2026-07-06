from backend.utils.constants import HarassmentCategory, SeverityLevel

_CRITICAL_SIGNALS = ("kill", "suicide", "self-harm", "weapon", "come to your house", "know where you live")
_HIGH_CATEGORIES = (HarassmentCategory.THREATS, HarassmentCategory.NON_CONSENSUAL_IMAGERY, HarassmentCategory.DOXXING)


def assess_severity(category: str, description: str, evidence_count: int = 0, is_repeat_reporter: bool = False) -> str:
    """Suggests a severity level for triage prioritization.

    Always err toward escalating rather than under-flagging - a false "critical"
    costs a counselor's time re-reviewing; a missed "critical" costs a student's
    safety. Staff can downgrade after review.
    """
    text = (description or "").lower()

    if any(signal in text for signal in _CRITICAL_SIGNALS):
        return SeverityLevel.CRITICAL

    if category in _HIGH_CATEGORIES:
        return SeverityLevel.HIGH

    if is_repeat_reporter or evidence_count >= 5:
        return SeverityLevel.HIGH

    if evidence_count >= 2:
        return SeverityLevel.MEDIUM

    return SeverityLevel.LOW
