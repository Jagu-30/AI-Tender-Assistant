import os
import hashlib
from fastapi import UploadFile
from app.core.config import settings

def calculate_file_hash(file_bytes: bytes) -> str:
    return hashlib.sha256(file_bytes).hexdigest()

async def save_uploaded_file(upload_file: UploadFile) -> tuple[str, str]:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    filename = os.path.basename(upload_file.filename or "uploaded_document.pdf")
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (".", "_", "-"))
    file_bytes = await upload_file.read()
    file_hash = calculate_file_hash(file_bytes)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{file_hash[:12]}_{safe_filename}")
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path, file_hash
