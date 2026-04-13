import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Email göndər. Uğurlu olduqda True, xəta olduqda False qaytarır.
    """
    message = Mail(
        from_email=settings.from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)
        if response.status_code not in (200, 202):
            logger.error("SendGrid xətası: status=%s", response.status_code)
            return False
        return True
    except Exception as exc:
        logger.exception("Email göndərilmədi: %s → %s", to_email, exc)
        return False


def send_phishing_email(to_email: str, subject: str, body_html: str, tracking_url: str) -> bool:
    """
    Phishing simulasiya emaili — tracking URL body-yə inject olunur.
    """
    tracked_body = body_html.replace("{{TRACKING_URL}}", tracking_url)
    return send_email(to_email, subject, tracked_body)


def send_training_email(to_email: str, employee_name: str, training_html: str) -> bool:
    """
    Klik basdıqdan sonra əməkdaşa göndərilən təlim emaili.
    """
    subject = "LionSafe: Vacib Təhlükəsizlik Bildirişi"
    body = training_html.replace("{{NAME}}", employee_name)
    return send_email(to_email, subject, body)
