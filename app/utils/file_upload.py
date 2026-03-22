import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def get_upload_path(folder: str) -> Path:
    path = Path(settings.UPLOAD_DIR) / folder
    path.mkdir(parents=True, exist_ok=True)
    return path


async def save_upload_file(file: UploadFile, folder: str) -> str:
    """Faylni saqlaydi va URL qaytaradi"""
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Faqat rasm fayllar qabul qilinadi: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Yaroqsiz fayl kengaytmasi")

    # Fayl hajmini tekshirish
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fayl hajmi {settings.MAX_FILE_SIZE // 1024 // 1024}MB dan oshmasligi kerak"
        )

    # Noyob fayl nomi
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_path = get_upload_path(folder)
    file_path = upload_path / filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    return f"/uploads/{folder}/{filename}"


def delete_file(file_url: str) -> None:
    """Faylni o'chiradi"""
    if not file_url or file_url.startswith("http"):
        return
    file_path = Path(file_url.lstrip("/"))
    if file_path.exists():
        file_path.unlink()
