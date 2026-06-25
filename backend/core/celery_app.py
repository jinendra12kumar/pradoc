from celery import Celery
from core.config import settings

celery_app = Celery(
    "pradoc",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
    include=["tasks.email_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "tasks.email_tasks.send_otp_email": {"queue": "email_queue"},
    },
)
