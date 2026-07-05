"""
Email Service — HTML templates for all notification types
"""
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.config import settings

logger = logging.getLogger(__name__)

BRAND_COLOR = "#6366f1"
BRAND_TEAL  = "#0891b2"

# ─── Shared layout wrapper ────────────────────────────────────────────────────
def _wrap(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;padding:40px 0;">
    <tr><td align="center">
      <table width="580" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08);">
        <tr>
          <td style="background:linear-gradient(135deg,{BRAND_COLOR},{BRAND_TEAL});padding:28px 40px;text-align:center;">
            <h1 style="margin:0;color:#fff;font-size:24px;font-weight:800;">🏥 PraDoc Health</h1>
            <p style="margin:6px 0 0;color:rgba(255,255,255,.85);font-size:13px;">{title}</p>
          </td>
        </tr>
        <tr><td style="padding:36px 40px;">{body}</td></tr>
        <tr>
          <td style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:16px 40px;text-align:center;">
            <p style="margin:0;color:#94a3b8;font-size:12px;">© 2026 PraDoc Health · All rights reserved</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _info_row(icon: str, label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding:8px 12px;font-size:13px;color:#64748b;">{icon} {label}</td>
      <td style="padding:8px 12px;font-size:13px;font-weight:700;color:#1e293b;">{value}</td>
    </tr>"""


def _appt_table(rows: list[tuple]) -> str:
    rows_html = "".join([_info_row(*r) for r in rows])
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;margin:20px 0;">
      {rows_html}
    </table>"""


# ─── OTP Email ────────────────────────────────────────────────────────────────
def _build_otp_html(full_name: str, otp: str, role: str) -> str:
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 12px;">Hi <strong>{full_name}</strong>,</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 24px;line-height:1.6;">
      Use the OTP below to complete your <strong>{role.capitalize()}</strong> registration. Valid for <strong>5 minutes</strong>.
    </p>
    <div style="background:#eef2ff;border:2px solid {BRAND_COLOR};border-radius:12px;padding:28px;text-align:center;margin:0 0 24px;">
      <p style="margin:0 0 6px;color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:2px;font-weight:600;">Your OTP</p>
      <p style="margin:0;color:{BRAND_COLOR};font-size:44px;font-weight:800;letter-spacing:12px;">{otp}</p>
      <p style="margin:10px 0 0;color:#94a3b8;font-size:12px;">Do not share this with anyone</p>
    </div>
    <p style="color:#94a3b8;font-size:13px;">If you did not request this, please ignore this email.</p>"""
    return _wrap(f"{role.capitalize()} Email Verification", body)


# ─── Appointment Booked ───────────────────────────────────────────────────────
def _build_appointment_booked_html(
    patient_name: str, doctor_name: str, date: str, time: str,
    clinic: str, fee: str, consult_type: str,
) -> str:
    rows = [
        ("👨‍⚕️", "Doctor", f"Dr. {doctor_name}"),
        ("🏥", "Clinic", clinic),
        ("📅", "Date", date),
        ("🕐", "Time", time),
        ("💊", "Type", consult_type.replace("_", " ").title()),
        ("💰", "Fee", f"₹{fee}"),
    ]
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 8px;">Hi <strong>{patient_name}</strong> 👋</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 20px;line-height:1.6;">
      Your appointment has been <strong style="color:{BRAND_COLOR};">successfully booked</strong> and is awaiting doctor confirmation.
    </p>
    {_appt_table(rows)}
    <div style="background:#fef3c7;border-radius:10px;padding:14px 18px;margin-top:4px;">
      <p style="margin:0;font-size:13px;color:#92400e;">⏳ Status is <strong>Pending</strong> — you'll get an email once the doctor confirms.</p>
    </div>"""
    return _wrap("Appointment Booked ✅", body)


# ─── Appointment Confirmed ────────────────────────────────────────────────────
def _build_appointment_confirmed_html(
    patient_name: str, doctor_name: str, date: str, time: str, clinic: str,
) -> str:
    rows = [
        ("👨‍⚕️", "Doctor", f"Dr. {doctor_name}"),
        ("🏥", "Clinic", clinic),
        ("📅", "Date", date),
        ("🕐", "Time", time),
    ]
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 8px;">Hi <strong>{patient_name}</strong> 🎉</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 20px;line-height:1.6;">
      Great news! Your appointment has been <strong style="color:#059669;">confirmed</strong>.
    </p>
    {_appt_table(rows)}
    <div style="background:#d1fae5;border-radius:10px;padding:14px 18px;margin-top:4px;">
      <p style="margin:0;font-size:13px;color:#065f46;">✅ Please arrive 10 minutes early. Carry your previous records if applicable.</p>
    </div>"""
    return _wrap("Appointment Confirmed ✅", body)


# ─── Appointment Cancelled ────────────────────────────────────────────────────
def _build_appointment_cancelled_html(
    recipient_name: str, doctor_name: str, date: str, time: str, reason: str | None,
) -> str:
    reason_line = f'<p style="color:#64748b;font-size:13px;margin-top:12px;">Reason: <em>{reason}</em></p>' if reason else ""
    rows = [
        ("👨‍⚕️", "Doctor", f"Dr. {doctor_name}"),
        ("📅", "Date", date),
        ("🕐", "Time", time),
    ]
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 8px;">Hi <strong>{recipient_name}</strong>,</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 20px;line-height:1.6;">
      Your appointment has been <strong style="color:#dc2626;">cancelled</strong>.
    </p>
    {_appt_table(rows)}
    {reason_line}
    <div style="background:#fee2e2;border-radius:10px;padding:14px 18px;margin-top:12px;">
      <p style="margin:0;font-size:13px;color:#991b1b;">If this was unexpected, please rebook or contact support.</p>
    </div>"""
    return _wrap("Appointment Cancelled ❌", body)


# ─── Prescription Uploaded ────────────────────────────────────────────────────
def _build_prescription_html(
    patient_name: str, doctor_name: str, diagnosis: str,
    medicines: list[dict], follow_up: str | None,
) -> str:
    med_rows = "".join([
        f'<tr><td style="padding:6px 10px;font-size:13px;color:#1e293b;border-bottom:1px solid #f1f5f9;"><strong>{m.get("name","")}</strong></td>'
        f'<td style="padding:6px 10px;font-size:13px;color:#64748b;">{m.get("dosage","")}</td>'
        f'<td style="padding:6px 10px;font-size:13px;color:#6366f1;">{m.get("frequency","")}</td>'
        f'<td style="padding:6px 10px;font-size:13px;color:#0f766e;">{m.get("duration","")}</td></tr>'
        for m in (medicines or [])
    ])
    followup_line = f'<p style="margin-top:14px;font-size:13px;color:#6366f1;font-weight:700;">🗓️ Follow-up: {follow_up}</p>' if follow_up else ""
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 8px;">Hi <strong>{patient_name}</strong> 💊</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 20px;line-height:1.6;">
      Dr. <strong>{doctor_name}</strong> has uploaded a prescription for you.
    </p>
    <div style="background:#eef2ff;border-radius:10px;padding:14px 18px;margin-bottom:16px;">
      <p style="margin:0;font-size:14px;color:#1e293b;"><strong>Diagnosis:</strong> {diagnosis}</p>
    </div>
    <table width="100%" cellpadding="0" cellspacing="0"
           style="background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;">
      <thead>
        <tr style="background:#f1f5f9;">
          <th style="padding:8px 10px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;">Medicine</th>
          <th style="padding:8px 10px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;">Dosage</th>
          <th style="padding:8px 10px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;">Freq</th>
          <th style="padding:8px 10px;text-align:left;font-size:11px;color:#64748b;text-transform:uppercase;">Duration</th>
        </tr>
      </thead>
      <tbody>{med_rows}</tbody>
    </table>
    {followup_line}
    <p style="margin-top:20px;font-size:13px;color:#94a3b8;">Log in to PraDoc to view and download your full prescription.</p>"""
    return _wrap("Prescription Ready 💊", body)


# ─── Medical Record Uploaded ──────────────────────────────────────────────────
def _build_record_uploaded_html(patient_name: str, record_title: str, record_type: str) -> str:
    body = f"""
    <p style="color:#1a2e3b;font-size:16px;margin:0 0 8px;">Hi <strong>{patient_name}</strong>,</p>
    <p style="color:#4a5568;font-size:15px;margin:0 0 20px;line-height:1.6;">
      Your medical record has been successfully uploaded to PraDoc.
    </p>
    <div style="background:#f0fdf4;border:1px solid #86efac;border-radius:12px;padding:20px 24px;">
      <p style="margin:0 0 6px;font-size:13px;color:#64748b;">Record Title</p>
      <p style="margin:0;font-size:16px;font-weight:800;color:#1e293b;">📁 {record_title}</p>
      <p style="margin:8px 0 0;font-size:12px;color:#0f766e;font-weight:600;">Type: {record_type.replace("_"," ").title()}</p>
    </div>
    <p style="margin-top:20px;font-size:13px;color:#94a3b8;">You can view all your records in the PraDoc patient portal under <strong>My Profile → Medical Records</strong>.</p>"""
    return _wrap("Medical Record Uploaded 📁", body)


# ─── Core SMTP sender ─────────────────────────────────────────────────────────
def _send(to: str, subject: str, html: str) -> None:
    if not settings.GMAIL or not settings.APPPASSWORD:
        logger.warning("Gmail not configured. Subject: %s", subject)
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{settings.EMAIL_FROM_NAME} <{settings.GMAIL}>"
    msg["To"]      = to
    msg.attach(MIMEText(html, "html", "utf-8"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(settings.GMAIL, settings.APPPASSWORD)
            s.sendmail(settings.GMAIL, [to], msg.as_string())
        logger.info("Email sent to %s — %s", to, subject)
    except smtplib.SMTPException as exc:
        logger.error("SMTP error to %s: %s", to, exc)
        raise


# ─── Public send functions (called from Celery tasks) ────────────────────────
def send_otp_email_sync(email: str, full_name: str, otp: str, role: str = "patient") -> None:
    _send(email, f"[PraDoc] Your OTP: {otp}", _build_otp_html(full_name, otp, role))


def send_appointment_booked_email(
    email: str, patient_name: str, doctor_name: str,
    date: str, time: str, clinic: str, fee: str, consult_type: str,
) -> None:
    html = _build_appointment_booked_html(patient_name, doctor_name, date, time, clinic, fee, consult_type)
    _send(email, "✅ Appointment Booked — PraDoc", html)


def send_appointment_confirmed_email(
    email: str, patient_name: str, doctor_name: str,
    date: str, time: str, clinic: str,
) -> None:
    html = _build_appointment_confirmed_html(patient_name, doctor_name, date, time, clinic)
    _send(email, "✅ Appointment Confirmed — PraDoc", html)


def send_appointment_cancelled_email(
    email: str, recipient_name: str, doctor_name: str,
    date: str, time: str, reason: str | None = None,
) -> None:
    html = _build_appointment_cancelled_html(recipient_name, doctor_name, date, time, reason)
    _send(email, "❌ Appointment Cancelled — PraDoc", html)


def send_prescription_email(
    email: str, patient_name: str, doctor_name: str,
    diagnosis: str, medicines: list, follow_up: str | None = None,
) -> None:
    html = _build_prescription_html(patient_name, doctor_name, diagnosis, medicines, follow_up)
    _send(email, "💊 Your Prescription is Ready — PraDoc", html)


def send_record_uploaded_email(
    email: str, patient_name: str, record_title: str, record_type: str,
) -> None:
    html = _build_record_uploaded_html(patient_name, record_title, record_type)
    _send(email, "📁 Medical Record Uploaded — PraDoc", html)
