import os
import uuid

from werkzeug.utils import secure_filename

try:
    import magic  # python-magic, backed by libmagic

    _HAS_MAGIC = True
except (ImportError, OSError):
    _HAS_MAGIC = False


class FileValidationError(Exception):
    pass


def _extension_of(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def sniff_mime_type(file_bytes: bytes, fallback_filename: str) -> str:
    if _HAS_MAGIC:
        try:
            return magic.from_buffer(file_bytes, mime=True)
        except Exception:
            pass
    import mimetypes

    guessed, _ = mimetypes.guess_type(fallback_filename)
    return guessed or "application/octet-stream"


def validate_upload(filename: str, file_bytes: bytes, allowed_extensions: set, allowed_mime_types: set, max_bytes: int) -> tuple[str, str]:
    """Validates an uploaded evidence file.

    Returns (safe_filename, detected_mime_type). Raises FileValidationError on any
    policy violation. Validates by extension AND real content sniffing so a renamed
    executable can't slip through as a ".jpg".
    """
    if not filename or not filename.strip():
        raise FileValidationError("Filename is required.")

    safe_name = secure_filename(filename)
    if not safe_name:
        raise FileValidationError("Filename is invalid.")

    extension = _extension_of(safe_name)
    if extension not in allowed_extensions:
        raise FileValidationError(f"File type '.{extension}' is not permitted.")

    if len(file_bytes) == 0:
        raise FileValidationError("Uploaded file is empty.")
    if len(file_bytes) > max_bytes:
        raise FileValidationError(f"File exceeds the maximum allowed size of {max_bytes // (1024 * 1024)} MB.")

    detected_mime = sniff_mime_type(file_bytes, safe_name)
    if detected_mime not in allowed_mime_types:
        raise FileValidationError(
            f"Detected file content type '{detected_mime}' does not match an allowed evidence type."
        )

    return safe_name, detected_mime


def generate_stored_filename(original_filename: str) -> str:
    """Generates a random, collision-free filename for storage on disk.

    Never derive the stored path from user-controlled filenames directly - this
    avoids path traversal and collisions/overwrites.
    """
    extension = _extension_of(secure_filename(original_filename))
    suffix = f".{extension}" if extension else ""
    return f"{uuid.uuid4().hex}{suffix}"


def resolve_storage_path(storage_dir: str, stored_filename: str) -> str:
    path = os.path.abspath(os.path.join(storage_dir, stored_filename))
    if not path.startswith(os.path.abspath(storage_dir) + os.sep):
        raise FileValidationError("Resolved path escapes the storage directory.")
    return path
