from pydantic import BaseModel


class ChatHistoryDeleteResponse(BaseModel):
    success: bool
    message: str
    deleted_count: int
    user_hash: str
