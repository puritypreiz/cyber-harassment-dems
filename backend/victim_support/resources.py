from backend.utils.constants import NATIONAL_CRISIS_RESOURCES

_CATEGORY_RESOURCES = {
    "non_consensual_imagery": [
        {"name": "StopNCII.org", "contact": "https://stopncii.org", "available": "Online image-removal tool"},
        {"name": "Cyber Civil Rights Initiative Safety Center", "contact": "https://cybercivilrights.org/ccri-safety-center/", "available": "Online resources"},
    ],
    "cyberstalking": [
        {"name": "National Center for Victims of Crime - Stalking Resource Center", "contact": "https://victimsofcrime.org/stalking-resource-center/", "available": "Online resources"},
    ],
    "doxxing": [
        {"name": "Data removal / deletion guide", "contact": "https://www.privacyrights.org", "available": "Online resources"},
    ],
}


def get_resources_for_category(category: str | None) -> list[dict]:
    resources = list(NATIONAL_CRISIS_RESOURCES)
    resources.extend(_CATEGORY_RESOURCES.get(category, []))
    return resources


def get_campus_resources(campus_config: dict | None = None) -> list[dict]:
    """Placeholder for institution-specific resources (Title IX office, campus
    security, on-campus counseling center) - populate via admin configuration
    per deployment rather than hardcoding one institution's contacts."""
    return campus_config.get("resources", []) if campus_config else []
