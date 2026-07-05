"""
Celery Tasks — Email notification workers for all appointment events
"""
import logging
from core.celery_app import celery_app
from services.email_service import (
    send_otp_email_sync,
    send_appointment_booked_email,
    send_appointment_confirmed_email,
    send_appointment_cancelled_email,
    send_prescription_email,
    send_record_uploaded_email,
)

logger = logging.getLogger(__name__)


def _retry(self, exc):
    raise self.retry(exc=exc, max_retries=3, countdown=10)


# ─── OTP ──────────────────────────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_otp_email", bind=True)
def send_otp_email(self, email: str, full_name: str, otp: str, role: str = "patient") -> None:
    """Send OTP verification email."""
    try:
        send_otp_email_sync(email=email, full_name=full_name, otp=otp, role=role)
    except Exception as exc:
        logger.error("OTP email failed for %s: %s", email, exc)
        _retry(self, exc)


# ─── Appointment Booked ───────────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_appointment_booked", bind=True)
def send_appointment_booked(
    self, email: str, patient_name: str, doctor_name: str,
    date: str, time: str, clinic: str, fee: str, consult_type: str,
) -> None:
    """Notify patient that their appointment was booked."""
    try:
        send_appointment_booked_email(email, patient_name, doctor_name, date, time, clinic, fee, consult_type)
    except Exception as exc:
        logger.error("Appointment booked email failed for %s: %s", email, exc)
        _retry(self, exc)


# ─── Appointment Confirmed ────────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_appointment_confirmed", bind=True)
def send_appointment_confirmed(
    self, email: str, patient_name: str, doctor_name: str,
    date: str, time: str, clinic: str,
) -> None:
    """Notify patient that their appointment was confirmed."""
    try:
        send_appointment_confirmed_email(email, patient_name, doctor_name, date, time, clinic)
    except Exception as exc:
        logger.error("Confirmed email failed for %s: %s", email, exc)
        _retry(self, exc)


# ─── Appointment Cancelled ────────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_appointment_cancelled", bind=True)
def send_appointment_cancelled(
    self, email: str, recipient_name: str, doctor_name: str,
    date: str, time: str, reason: str | None = None,
) -> None:
    """Notify patient/doctor that an appointment was cancelled."""
    try:
        send_appointment_cancelled_email(email, recipient_name, doctor_name, date, time, reason)
    except Exception as exc:
        logger.error("Cancelled email failed for %s: %s", email, exc)
        _retry(self, exc)


# ─── Prescription Ready ───────────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_prescription_ready", bind=True)
def send_prescription_ready(
    self, email: str, patient_name: str, doctor_name: str,
    diagnosis: str, medicines: list, follow_up: str | None = None,
) -> None:
    """Notify patient that a prescription has been created."""
    try:
        send_prescription_email(email, patient_name, doctor_name, diagnosis, medicines, follow_up)
    except Exception as exc:
        logger.error("Prescription email failed for %s: %s", email, exc)
        _retry(self, exc)


# ─── Medical Record Uploaded ──────────────────────────────────────────────────
@celery_app.task(name="tasks.email_tasks.send_record_uploaded", bind=True)
def send_record_uploaded(
    self, email: str, patient_name: str, record_title: str, record_type: str,
) -> None:
    """Notify patient that a medical record was uploaded."""
    try:
        send_record_uploaded_email(email, patient_name, record_title, record_type)
    except Exception as exc:
        logger.error("Record uploaded email failed for %s: %s", email, exc)
        _retry(self, exc)
