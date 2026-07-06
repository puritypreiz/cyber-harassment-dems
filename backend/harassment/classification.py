"""Lightweight keyword-assisted classification.

This is a triage aid, not a determination of fact - staff always review and can
override the suggested category. Avoiding an opaque ML model here keeps the
decision auditable and explainable to the student and to counselors/legal staff.
"""
from backend.utils.constants import HarassmentCategory

_KEYWORDS = {
    HarassmentCategory.CYBERSTALKING: ("stalk", "following me", "tracking my location", "shows up wherever"),
    HarassmentCategory.NON_CONSENSUAL_IMAGERY: ("nude", "intimate photo", "leaked photo", "revenge porn", "deepfake"),
    HarassmentCategory.DOXXING: ("posted my address", "posted my home address", "shared my phone number", "leaked my info", "doxx"),
    HarassmentCategory.IMPERSONATION: ("fake account", "pretending to be me", "impersonat"),
    HarassmentCategory.THREATS: ("kill you", "hurt you", "i'll find you", "threat"),
    HarassmentCategory.SEXUAL_HARASSMENT: ("sexual", "send nudes", "unwanted advances"),
    HarassmentCategory.HATE_SPEECH: ("slur", "hate speech", "racist", "homophobic"),
    HarassmentCategory.DEFAMATION: ("spreading lies", "false rumors", "defam"),
}


def suggest_category(description: str) -> str:
    text = (description or "").lower()
    scores = {
        category: sum(1 for kw in keywords if kw in text)
        for category, keywords in _KEYWORDS.items()
    }
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else HarassmentCategory.OTHER
