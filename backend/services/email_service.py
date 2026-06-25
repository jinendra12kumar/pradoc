import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core.config import settings

logger = logging.getLogger(__name__)


def _build_otp_html(full_name: str, otp: str, role: str) -> str:
    role_label = role.capitalize()
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f0f9ff;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f9ff;padding:40px 0;">
    <tr><td align="center">
      <table width="580" cellpadding="0" cellspacing="0"
             style="background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,180,160,.12);">
        <tr>
          <td style="background:linear-gradient(135deg,#00c8b4,#0098e5);padding:32px 40px;text-align:center;">
            <h1 style="margin:0;color:#fff;font-size:26px;font-weight:700;">🏥 PraDoc Health</h1>
            <p style="margin:8px 0 0;color:rgba(255,255,255,.85);font-size:13px;">{role_label} Email Verification</p>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <p style="color:#1a2e3b;font-size:16px;margin:0 0 12px;">Hi <strong>{full_name}</strong>,</p>
            <p style="color:#4a5568;font-size:15px;margin:0 0 28px;line-height:1.6;">
              Use the OTP below to complete your <strong>{role_label}</strong> registration.
              It is valid for <strong>5 minutes</strong>.
            </p>
            <div style="background:#f0fffe;border:2px solid #00c8b4;border-radius:12px;
                        padding:28px;text-align:center;margin:0 0 28px;">
              <p style="margin:0 0 6px;color:#4a5568;font-size:12px;text-transform:uppercase;
                        letter-spacing:2px;font-weight:600;">Your OTP</p>
              <p style="margin:0;color:#00c8b4;font-size:44px;font-weight:800;letter-spacing:12px;">{otp}</p>
              <p style="margin:10px 0 0;color:#718096;font-size:12px;">Do not share this with anyone</p>
            </div>
            <p style="color:#a0aec0;font-size:13px;">
              If you did not request this, please ignore this email.
            </p>
          </td>
        </tr>
        <tr>
          <td style="background:#f8fdff;border-top:1px solid #e2f4f1;padding:18px 40px;text-align:center;">
            <p style="margin:0;color:#a0aec0;font-size:12px;">© 2026 PraDoc Health. All rights reserved.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_otp_email_sync(email: str, full_name: str, otp: str, role: str = "patient") -> None:
    """
    Send OTP email via Gmail SMTP (synchronous — called from Celery worker).
    """
    if not settings.GMAIL or not settings.APPPASSWORD:
        logger.warning("Gmail credentials not configured. OTP: %s", otp)
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[PraDoc] Your OTP: {otp}"
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.GMAIL}>"
    msg["To"] = email

    html_part = MIMEText(_build_otp_html(full_name, otp, role), "html", "utf-8")
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.GMAIL, settings.APPPASSWORD)
            server.sendmail(settings.GMAIL, [email], msg.as_string())
        logger.info("OTP email sent to %s", email)
    except smtplib.SMTPException as exc:
        logger.error("Failed to send OTP email to %s: %s", email, exc)
        raise
