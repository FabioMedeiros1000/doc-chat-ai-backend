"""Deletes rows from Agno-managed tables (default session table name)."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def delete_agno_sessions_for_user(session: Session, user_id: str) -> int:
    """Remove persisted Agno sessions for the given user_id (same value as chat userHash).

    Table name matches Agno MySQLDb default; see https://docs.agno.com/database/session-storage
    """
    result = session.execute(
        text("DELETE FROM agno_sessions WHERE user_id = :user_id"),
        {"user_id": user_id},
    )
    return int(result.rowcount or 0)
