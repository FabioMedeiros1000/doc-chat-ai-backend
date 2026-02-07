from typing import Literal, Optional

from pydantic import BaseModel


class FileItem(BaseModel):
    id: str
    name: str
    size: int
    uploadedAt: str
    status: Optional[Literal["processing", "ready", "error"]] = None
