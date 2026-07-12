import os
import re
from flask import current_app


def is_allowed_extension(filename: str) -> bool:
    if not filename:
        return False
    if '.' not in filename:
        return False
    return filename.rsplit('.', 1)[1].lower() in set(current_app.config.get('ALLOWED_UPLOAD_EXTENSIONS', set()))


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def is_valid_email(email: str) -> bool:
    return bool(re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', normalize_email(email)))


def save_uploaded_file(uploaded_file, folder: str, prefix: str = "") -> str:
    if not uploaded_file or not uploaded_file.filename:
        return ""
    from werkzeug.utils import secure_filename
    import uuid
    import time

    original_name = secure_filename(uploaded_file.filename)
    if not original_name:
        return ""
    ts = int(time.time())
    uid = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{ts}_{uid}_{original_name}" if prefix else f"{ts}_{uid}_{original_name}"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    uploaded_file.save(path)
    return filename
