from typing import Optional

from pydantic import BaseModel


class DeleteResponse(BaseModel):
    success: bool
    message: str
    content_hash: Optional[str] = None
