from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from db.base import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    job_id = Column(String(64), primary_key=True)
    user_hash = Column(String(128), nullable=False, index=True)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024), nullable=False)
    content_type = Column(String(255), nullable=True)
    size = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    content_hash = Column(String(128), nullable=True, index=True)
    metadata_hash = Column(String(128), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
