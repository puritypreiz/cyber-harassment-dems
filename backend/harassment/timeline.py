from backend.chain_of_custody.evidence_history import get_case_history


def build_case_timeline(case) -> list[dict]:
    entries = get_case_history(case.id)
    timeline = [
        {
            "timestamp": entry.created_at.isoformat(),
            "action": entry.action,
            "actor_id": entry.actor_id,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "details": entry.details,
        }
        for entry in entries
    ]
    timeline.sort(key=lambda item: item["timestamp"])
    return timeline
