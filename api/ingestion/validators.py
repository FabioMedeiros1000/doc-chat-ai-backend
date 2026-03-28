from __future__ import annotations

from pathlib import Path

from api.exceptions import AgentError
from api.ingestion.constants import ALLOWED_EXTENSIONS, ERROR_UNSUPPORTED_FORMAT


class UploadValidator:
    def __init__(self, allowed_extensions: set[str] | None = None) -> None:
        self._allowed_extensions = allowed_extensions or ALLOWED_EXTENSIONS

    def validate_extension(self, filename: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext not in self._allowed_extensions:
            raise AgentError(ERROR_UNSUPPORTED_FORMAT)
        return ext
