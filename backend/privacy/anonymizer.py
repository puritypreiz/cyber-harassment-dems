import io

from PIL import Image


def anonymize_case_dict(case_dict: dict) -> dict:
    """Removes reporter-identifying fields from a case payload when the reporter
    filed anonymously. Used whenever a case is shown to anyone other than the
    reporter themselves or staff with a legitimate need (counselor/legal/admin).
    """
    if not case_dict.get("is_anonymous"):
        return case_dict
    redacted = dict(case_dict)
    redacted.pop("reporter_id", None)
    return redacted


def mask_email(email: str) -> str:
    if "@" not in email:
        return "***"
    local, _, domain = email.partition("@")
    if len(local) <= 2:
        masked_local = "*" * len(local)
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def strip_image_exif(image_bytes: bytes) -> bytes:
    """Returns a copy of the image with all EXIF metadata (including GPS location)
    removed - used when generating shareable/exported copies of evidence so a
    student's location history isn't leaked to whoever the report is shared with.
    The original, unmodified evidence file and its hash are never altered.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        data = list(img.getdata())
        stripped = Image.new(img.mode, img.size)
        stripped.putdata(data)
        buffer = io.BytesIO()
        stripped.save(buffer, format=img.format or "PNG")
        return buffer.getvalue()
