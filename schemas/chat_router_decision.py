from enum import Enum

from pydantic import BaseModel


class ChatRoute(str, Enum):
    SOCIAL = "SOCIAL"
    KNOWLEDGE = "KNOWLEDGE"


class ChatRouterDecision(BaseModel):
    route: ChatRoute
    reason: str
    answer: str | None = None
