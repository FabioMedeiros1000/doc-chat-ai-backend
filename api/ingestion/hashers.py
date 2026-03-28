from __future__ import annotations

import hashlib


class ContentHasher:
    def compute_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def compute_metadata_hash(self, filename: str, content_type: str | None, size: int) -> str:
        normalized_name = (filename or "").strip().lower()
        normalized_type = (content_type or "").strip().lower()
        payload = f"{normalized_name}|{normalized_type}|{size}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
