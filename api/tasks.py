from celery_app import celery_app

from api.services import LeiService


@celery_app.task(name="process_upload")
def process_upload(job_id: str, api_key: str | None = None) -> None:
    service = LeiService()
    service.process_upload_job(job_id, api_key=api_key)
