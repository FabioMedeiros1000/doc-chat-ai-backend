import hashlib
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from api.exceptions import AgentError
from api.ingestion.constants import (
    ALLOWED_EXTENSIONS,
    ERROR_EMPTY_FILE,
    ERROR_UNSUPPORTED_FORMAT,
    UPLOAD_SOURCE,
)


def validate_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise AgentError(ERROR_UNSUPPORTED_FORMAT)
    return ext


async def read_upload_data(file: UploadFile) -> bytes:
    data = await file.read()
    if not data:
        raise AgentError(ERROR_EMPTY_FILE)
    return data


def write_temp_bytes(data: bytes, suffix: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(data)
        return Path(tmp.name)


def write_temp_markdown(text: str) -> Path:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as md:
        md.write(text.encode("utf-8"))
        return Path(md.name)


def compute_text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_metadata(filename: str, content_type: Optional[str], content_hash: str) -> dict:
    return {
        "filename": filename,
        "content_type": content_type,
        "source": UPLOAD_SOURCE,
        "hash": content_hash,
    }


def cleanup_paths(*paths: Optional[Path]) -> None:
    for path in paths:
        if path and path.exists():
            path.unlink(missing_ok=True)
