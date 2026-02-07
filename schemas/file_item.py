from typing import Literal, Optional

from pydantic import BaseModel


class FileItem(BaseModel):
    id: str
    name: str
