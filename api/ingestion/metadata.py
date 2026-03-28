from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from api.ingestion.constants import UPLOAD_SOURCE


class MetadataBuilder:
    def _utc_now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def build_metadata(
        self,
        filename: str,
        content_type: Optional[str],
        content_hash: str,
        user_hash: str,
        size: int,
        uploaded_at: Optional[str] = None,
        status: str = "ready",
    ) -> dict:
        uploaded_at_value = uploaded_at or self._utc_now_iso()
        return {
            "filename": filename,
            "content_type": content_type,
            "source": UPLOAD_SOURCE,
            "hash": content_hash,
            "user_hash": user_hash,
            "size": size,
            "uploaded_at": uploaded_at_value,
            "status": status,
        }
