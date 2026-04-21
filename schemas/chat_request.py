from pydantic import BaseModel, field_validator

class ChatRequest(BaseModel):
    question: str
    userHash: str
    documentIds: list[str] | None = None

    @field_validator("documentIds")
    @classmethod
    def normalize_document_ids(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None

        normalized: list[str] = []
        seen: set[str] = set()
        for item in value:
            current = item.strip()
            if not current or current in seen:
                continue
            seen.add(current)
            normalized.append(current)
        return normalized
