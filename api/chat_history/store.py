from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select

from api.exceptions import AgentError
from db.models import ChatMessage
from db.session import get_session
from schemas.chat_message_item import ChatMessageItem


class ChatHistoryStore:
    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc)

    def create_message(
        self,
        *,
        user_hash: str,
        role: str,
        content: str,
        status: str,
        model: Optional[str] = None,
        run_id: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> ChatMessage:
        normalized_user_hash = user_hash.strip() if user_hash else ""
        if not normalized_user_hash:
            raise AgentError("userHash is required.")

        if role not in {"user", "assistant"}:
            raise AgentError("Invalid chat message role.")

        if not content:
            raise AgentError("content is required.")

        message = ChatMessage(
            user_hash=normalized_user_hash,
            role=role,
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            model=model,
            status=status,
            error_message=error_message,
            run_id=run_id,
            created_at=self._utc_now(),
        )

        session = get_session()
        try:
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
        finally:
            session.close()

    def get_messages_for_user(self, user_hash: str) -> List[ChatMessageItem]:
        normalized_user_hash = user_hash.strip() if user_hash else ""
        if not normalized_user_hash:
            raise AgentError("userHash is required.")

        session = get_session()
        try:
            stmt = (
                select(ChatMessage)
                .where(ChatMessage.user_hash == normalized_user_hash)
                .order_by(ChatMessage.message_id.asc())
            )
            messages = list(session.execute(stmt).scalars().all())
        finally:
            session.close()

        return [
            ChatMessageItem(
                id=message.message_id,
                role=message.role,
                content=message.content,
                status=message.status,
                created_at=message.created_at,
            )
            for message in messages
        ]

    def get_total_tokens_for_user(self, user_hash: str) -> int:
        normalized_user_hash = user_hash.strip() if user_hash else ""
        if not normalized_user_hash:
            raise AgentError("userHash is required.")

        session = get_session()
        try:
            stmt = (
                select(func.coalesce(func.sum(ChatMessage.total_tokens), 0))
                .where(ChatMessage.user_hash == normalized_user_hash)
                .where(ChatMessage.role == "assistant")
                .where(ChatMessage.status == "completed")
            )
            result = session.execute(stmt).scalar_one()
            return int(result or 0)
        finally:
            session.close()

    def delete_messages_for_user(self, user_hash: str) -> int:
        normalized_user_hash = user_hash.strip() if user_hash else ""
        if not normalized_user_hash:
            raise AgentError("userHash is required.")

        session = get_session()
        try:
            count = (
                session.query(ChatMessage)
                .filter(ChatMessage.user_hash == normalized_user_hash)
                .delete(synchronize_session=False)
            )
            session.commit()
            return int(count or 0)
        finally:
            session.close()
