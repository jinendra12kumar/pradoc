"""
File Upload Service — local storage with future S3 migration path
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile, HTTPException, status
from core.config import settings


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class FileService:
    """Handles file storage and hash computation.

    Currently uses local disk. Replace this class with an S3-backed
    implementation for production — the interface stays identical.
    """

    def __init__(self) -> None:
        self.upload_root = Path(settings.UPLOAD_DIR)
        self.upload_root.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    async def save_upload(
        self,
        file: UploadFile,
        doctor_id: str,
        subfolder: str = "documents",
    ) -> Tuple[str, str, int]:
        """Save an uploaded file and return (file_path, file_hash, file_size).

        Raises HTTPException on invalid file type or size.
        """
        self._validate_extension(file.filename)

        # Read full content for hashing + size check
        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB.",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        file_hash = self._compute_hash(content)

        # Build path: uploads/<doctor_id>/<subfolder>/<unique_name>
        ext = Path(file.filename).suffix.lower()
        unique_name = f"{subfolder}_{uuid.uuid4().hex[:12]}_{int(datetime.utcnow().timestamp())}{ext}"
        dest_dir = self.upload_root / doctor_id / subfolder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / unique_name

        with open(dest_path, "wb") as f:
            f.write(content)

        # Return relative path from upload root (for DB storage)
        relative_path = f"{doctor_id}/{subfolder}/{unique_name}"
        return relative_path, file_hash, file_size

    async def delete_file(self, file_path: str) -> None:
        """Delete a file by its relative path."""
        full_path = self.upload_root / file_path
        if full_path.exists():
            full_path.unlink()

    def get_full_path(self, file_path: str) -> Path:
        """Resolve relative DB path to absolute path."""
        return self.upload_root / file_path

    # ── Internals ─────────────────────────────────────────────────────────────

    @staticmethod
    def _compute_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def _validate_extension(filename: str) -> None:
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No filename provided.",
            )
        ext = Path(filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )
