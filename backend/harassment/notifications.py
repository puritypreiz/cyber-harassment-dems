import smtplib
from email.mime.text import MIMEText

from flask import current_app

from backend.database.database import db
from backend.database.models.notification import Notification
from backend.utils.helpers import utcnow
from backend.utils.logger import get_app_logger

logger = get_app_logger()


def _send_email(to_email: str, subject: str, body: str) -> bool:
    config = current_app.config
    if not config.get("SMTP_HOST"):
        logger.info("SMTP not configured; email to %s logged only (dry-run).", to_email)
        return False

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = config["SMTP_SENDER"]
    message["To"] = to_email

    with smtplib.SMTP(config["SMTP_HOST"], config["SMTP_PORT"]) as server:
        server.starttls()
        if config.get("SMTP_USERNAME"):
            server.login(config["SMTP_USERNAME"], config["SMTP_PASSWORD"])
        server.sendmail(config["SMTP_SENDER"], [to_email], message.as_string())
    return True


def _send_sms(phone_number: str, body: str) -> bool:
    if not current_app.config.get("SMS_PROVIDER_API_KEY"):
        logger.info("SMS provider not configured; SMS to %s logged only (dry-run).", phone_number)
        return False
    # Wire in a real provider (e.g. Twilio) here. Kept as a stub so no vendor
    # credentials are hardcoded into the codebase.
    logger.info("SMS dispatch requested for %s (provider integration not implemented).", phone_number)
    return False


def notify(user, channel: str, subject: str, body: str, case_id: str | None = None) -> Notification:
    notification = Notification(user_id=user.id, case_id=case_id, channel=channel, subject=subject, body=body)
    db.session.add(notification)
    db.session.commit()

    try:
        if channel == "email":
            sent = _send_email(user.email, subject, body)
        elif channel == "sms":
            sent = _send_sms(getattr(user, "phone_number", None) or "", body)
        else:
            sent = False

        notification.status = "sent" if sent else "skipped"
        if sent:
            notification.sent_at = utcnow()
    except Exception:
        logger.exception("Notification dispatch failed for user %s", user.id)
        notification.status = "failed"

    db.session.commit()
    return notification


def notify_case_status_change(user, case) -> Notification:
    return notify(
        user,
        channel="email",
        subject=f"Update on your case #{case.case_number}",
        body=f"Your case status has changed to: {case.status}.",
        case_id=case.id,
    )


def notify_counselor_assigned(counselor, case) -> Notification:
    return notify(
        counselor,
        channel="email",
        subject=f"New case assigned: #{case.case_number}",
        body=f"You have been assigned as counselor for case #{case.case_number} (severity: {case.severity}).",
        case_id=case.id,
    )
