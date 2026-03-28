from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

from api.exceptions import AgentError, UserStorageLimitError
from api.ingestion.constants import ERROR_EMPTY_FILE, ERROR_FILE_TOO_LARGE
from api.ingestion.dtos import TempFileInfo


class UploadStorage:
    async def save_stream(
        self,
        file: UploadFile,
        suffix: str,
        max_bytes: Optional[int] = None,
    ) -> TempFileInfo:
        size = 0
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                tmp.write(chunk)
                size += len(chunk)
                if max_bytes is not None and size > max_bytes:
                    path = Path(tmp.name)
                    self.cleanup_paths(path)
                    raise UserStorageLimitError(ERROR_FILE_TOO_LARGE)
        if size == 0:
            path = Path(tmp.name)
            self.cleanup_paths(path)
            raise AgentError(ERROR_EMPTY_FILE)
        return TempFileInfo(path=Path(tmp.name), size=size)

    def write_temp_markdown(self, text: str) -> Path:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as md:
            md.write(text.encode("utf-8"))
            return Path(md.name)

    def cleanup_paths(self, *paths: Optional[Path]) -> None:
        for path in paths:
            if path and path.exists():
                path.unlink(missing_ok=True)
