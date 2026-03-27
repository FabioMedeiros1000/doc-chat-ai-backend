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
    file_path: str,
    metadata_hash: str,
) -> IngestionJob:
    job_id = f"job_{uuid4().hex}"
    now = _utc_now()
    job = IngestionJob(
        job_id=job_id,
        user_hash=user_hash,
        filename=filename,
        content_type=content_type,
        size=size,
        file_path=file_path,
        metadata_hash=metadata_hash,
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




def delete_jobs_for_user(user_hash: str, content_hash: str) -> int:
    session = get_session()
    try:
        count = (
            session.query(IngestionJob)
            .filter(IngestionJob.user_hash == user_hash)
            .filter(IngestionJob.content_hash == content_hash)
            .delete(synchronize_session=False)
        )
        session.commit()
        return int(count or 0)
    finally:
        session.close()

def get_job(job_id: str) -> Optional[IngestionJob]:
    session = get_session()
    try:
        return session.get(IngestionJob, job_id)
    finally:
        session.close()

def find_job_by_metadata_hash(user_hash: str, metadata_hash: str) -> Optional[IngestionJob]:
    session = get_session()
    try:
        statuses = ("queued", "processing", "ready")
        stmt = (
            select(IngestionJob)
            .where(IngestionJob.user_hash == user_hash)
            .where(IngestionJob.metadata_hash == metadata_hash)
            .where(IngestionJob.status.in_(statuses))
            .order_by(IngestionJob.updated_at.desc())
            .limit(1)
        )
        return session.execute(stmt).scalars().first()
    finally:
        session.close()

