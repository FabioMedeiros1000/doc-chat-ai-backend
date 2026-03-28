from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class TempFileInfo:
    path: Path
    size: int

@dataclass(frozen=True)
class UploadResult:
    success: bool
    message: str
    job_id: Optional[str] = None
    status: Optional[str] = None
    is_existing: bool = False
