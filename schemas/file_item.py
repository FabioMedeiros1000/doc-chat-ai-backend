from typing import Literal, Optional

from pydantic import BaseModel


class FileItem(BaseModel):
    id: Optional[str] = None
    name: str
    status: Literal["queued", "processing", "ready", "failed"] = "ready"
    job_id: Optional[str] = None
    error_message: Optional[str] = None
