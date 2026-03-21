from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import func, select

from db.models import IngestionJob
from db.session import get_session


def _utc_now() -> datetime:
    return datetime.utcnow()


def create_job(
    user_hash: str,
    filename: str,
    content_type: Optional[str],
    size: int,
) -> IngestionJob:
    job_id = f"job_{uuid4().hex}"
    now = _utc_now()
    job = IngestionJob(
        job_id=job_id,
        user_hash=user_hash,
        filename=filename,
        content_type=content_type,
        size=size,
        status="queued",
        error_message=None,
        content_hash=None,
        created_at=now,
        updated_at=now,
    )
    session = get_session()
    try:
        session.add(job)
        session.commit()
        session.refresh(job)
        return job
    finally:
        session.close()


def update_job(
    job_id: str,
    *,
    status: Optional[str] = None,
    error_message: Optional[str] = None,
    content_hash: Optional[str] = None,
) -> Optional[IngestionJob]:
    session = get_session()
    try:
        job = session.get(IngestionJob, job_id)
        if not job:
            return None
        if status is not None:
            job.status = status
        if error_message is not None:
            job.error_message = error_message
        if content_hash is not None:
            job.content_hash = content_hash
        job.updated_at = _utc_now()
        session.commit()
        session.refresh(job)
        return job
    finally:
        session.close()


def list_jobs_for_user(user_hash: str) -> List[IngestionJob]:
    session = get_session()
    try:
        stmt = select(IngestionJob).where(IngestionJob.user_hash == user_hash)
        return list(session.execute(stmt).scalars().all())
    finally:
        session.close()

def get_total_size_for_user(user_hash: str) -> int:
    session = get_session()
    try:
        statuses = ("queued", "processing", "ready")
        stmt = (
            select(func.coalesce(func.sum(IngestionJob.size), 0))
            .where(IngestionJob.user_hash == user_hash)
            .where(IngestionJob.status.in_(statuses))
        )
        result = session.execute(stmt).scalar_one()
        return int(result or 0)
    finally:
        session.close()

