import logging
from core.celery_app import celery_app
from services.email_service import send_otp_email_sync

logger = logging.getLogger(__name__)


@celery_app.task(
    name="tasks.email_tasks.send_otp_email",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
)
def send_otp_email(self, email: str, full_name: str, otp: str, role: str = "patient") -> None:
    """Celery task — sends OTP email via Gmail SMTP. Retries up to 3x on failure."""
    try:
        send_otp_email_sync(email=email, full_name=full_name, otp=otp, role=role)
    except Exception as exc:
        logger.error("Email task failed for %s: %s", email, exc)
        raise self.retry(exc=exc)
