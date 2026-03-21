from typing import Literal, Optional

from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    message: str
    job_id: Optional[str] = None
    status: Optional[Literal["queued", "processing"]] = None
