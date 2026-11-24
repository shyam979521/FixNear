"""
Upload service — one place that handles saving files safely, so every
route uses the exact same validation instead of duplicating it.
"""

import os
import uuid
from flask import current_app
from app.extensions import db
from app.models import UploadedImage

# Magic-byte signatures for the formats we actually allow. Checking these
# (rather than trusting the filename extension or the client-supplied
# Content-Type, both of which are trivially spoofable) confirms the
# uploaded bytes are really the image format they claim to be.
_MAGIC_BYTES = {
    "png": [b"\x89PNG\r\n\x1a\n"],
    "jpg": [b"\xff\xd8\xff"],
    "jpeg": [b"\xff\xd8\xff"],
    "gif": [b"GIF87a", b"GIF89a"],
    "webp": [b"RIFF"],  # followed by "WEBP" at offset 8, checked separately below
}


def _allowed_extension(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_IMAGE_EXTENSIONS"]


def _content_matches_extension(file_storage, ext):
    """
    SECURITY: verified before this fix that only the filename extension
    and the client-supplied (attacker-controlled) mimetype were checked —
    a non-image file simply renamed to end in `.png` passed validation
    completely. This reads the first few real bytes off disk and checks
    them against the known signature for the claimed format.
    """
    file_storage.stream.seek(0)
    header = file_storage.stream.read(12)
    file_storage.stream.seek(0)

    if ext == "webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"

    signatures = _MAGIC_BYTES.get(ext, [])
    return any(header.startswith(sig) for sig in signatures)


def save_uploaded_file(file_storage, uploaded_by=None, job_id=None):
    """
    Validates and saves an uploaded image.

    Returns the stored (random, collision-proof) filename, or None if no
    file was provided or it failed validation. The original filename is
    never trusted or reused for the path — only its extension is read,
    which rules out path-traversal and overwrite attacks by construction.
    """
    if not file_storage or file_storage.filename == "":
        return None

    original_name = file_storage.filename
    if not _allowed_extension(original_name):
        return None

    ext = original_name.rsplit(".", 1)[1].lower()
    if not _content_matches_extension(file_storage, ext):
        return None

    # Guard against oversized uploads even if MAX_CONTENT_LENGTH wasn't
    # enforced upstream (e.g. when called outside a normal request).
    file_storage.stream.seek(0, os.SEEK_END)
    size_bytes = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size_bytes > current_app.config["MAX_CONTENT_LENGTH"]:
        return None

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
    file_storage.save(save_path)

    record = UploadedImage(
        filename=unique_name,
        original_name=original_name,
        uploaded_by=uploaded_by,
        job_id=job_id,
        mime_type=file_storage.mimetype,
        size_bytes=size_bytes,
    )
    db.session.add(record)
    db.session.commit()

    return unique_name
