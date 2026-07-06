import io

from PIL import Image
from PIL.ExifTags import TAGS


def extract_metadata(file_bytes: bytes, mime_type: str) -> dict:
    """Extracts non-sensitive technical metadata for chain-of-custody records.

    Deliberately excludes GPS/location EXIF tags - those can de-anonymize a victim
    if the evidence record is ever exported or shared, and the case system already
    tracks upload time/location via the audit log with proper access controls.
    """
    metadata = {"mime_type": mime_type, "byte_size": len(file_bytes)}

    if mime_type.startswith("image/"):
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                metadata["width"] = img.width
                metadata["height"] = img.height
                metadata["format"] = img.format

                exif_data = img.getexif()
                if exif_data:
                    safe_exif = {}
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, str(tag_id))
                        if "GPS" in tag_name or tag_name in ("MakerNote",):
                            continue
                        if isinstance(value, (bytes, bytearray)):
                            continue
                        safe_exif[tag_name] = str(value)[:200]
                    if safe_exif:
                        metadata["exif"] = safe_exif
        except Exception:
            metadata["parse_warning"] = "Could not parse image metadata."

    return metadata
