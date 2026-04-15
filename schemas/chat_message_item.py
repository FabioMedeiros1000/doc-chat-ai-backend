from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ChatMessageItem(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    status: str
    created_at: datetime
