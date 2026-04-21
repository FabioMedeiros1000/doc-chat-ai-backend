from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Union

from agno.filters import FilterExpr
from agno.vectordb.qdrant import Qdrant
from qdrant_client.http import models


class FilteredQdrant(Qdrant):
    def __init__(self, *args, default_filters: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._default_filters = default_filters or {}

    def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Union[Dict[str, Any], List[FilterExpr]]] = None,
    ):
        merged_filters: Dict[str, Any] = dict(self._default_filters)
        if isinstance(filters, dict):
            merged_filters.update(filters)
        return super().search(query=query, limit=limit, filters=merged_filters)

    def _format_filters(self, filters: Optional[Dict[str, Any]]) -> Optional[models.Filter]:
        if not filters:
            return None

        filter_conditions = []
        for key, value in filters.items():
            if "." not in key and not key.startswith("meta_data."):
                key = f"meta_data.{key}"

            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    filter_conditions.append(
                        models.FieldCondition(key=f"{key}.{sub_key}", match=models.MatchValue(value=sub_value))
                    )
                continue

            if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
                values = [item for item in value if item is not None]
                if not values:
                    continue
                filter_conditions.append(
                    models.FieldCondition(key=key, match=models.MatchAny(any=values))
                )
                continue

            filter_conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=value)))

        if filter_conditions:
            return models.Filter(must=filter_conditions)  # type: ignore
        return None
