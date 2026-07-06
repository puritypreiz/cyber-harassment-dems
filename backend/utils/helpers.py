from datetime import datetime, timezone

from flask import request


def utcnow() -> datetime:
    """Naive UTC "now", for storing in / comparing against DateTime columns.

    SQLite has no timezone-aware datetime type: a value written as tz-aware comes
    back naive after a round-trip through the database. Standardizing on naive
    UTC everywhere avoids "can't compare offset-naive and offset-aware datetimes"
    crashes when a freshly-created value is compared against one just loaded
    from the database.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


def client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.remote_addr or "unknown"


def paginate_query(query, page: int = 1, per_page: int = 20, max_per_page: int = 100):
    page = max(page, 1)
    per_page = min(max(per_page, 1), max_per_page)
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, {"page": page, "per_page": per_page, "total": total}
