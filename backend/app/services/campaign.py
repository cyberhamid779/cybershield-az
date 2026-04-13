import secrets
import logging
from sqlalchemy.orm import Session

from app.config import settings
from app.models.campaign import Campaign
from app.models.click import Click
from app.models.user import User
from app.services.email import send_phishing_email

logger = logging.getLogger(__name__)


def launch_campaign(campaign_id: int, db: Session) -> dict:
    """
    Kampaniyanı başlat:
    1. Hər əməkdaş üçün unikal token yarat
    2. Click qeydi yarat
    3. Phishing email göndər
    """
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise ValueError(f"Kampaniya tapılmadı: {campaign_id}")

    employees = db.query(User).filter(
        User.org_id == campaign.org_id,
        User.is_admin == False,
    ).all()

    if not employees:
        raise ValueError("Bu təşkilatda əməkdaş yoxdur")

    sent, failed = 0, 0

    for employee in employees:
        token = secrets.token_urlsafe(32)
        tracking_url = f"{settings.base_url}/t/{token}"

        click = Click(
            user_id=employee.id,
            campaign_id=campaign.id,
            token=token,
        )
        db.add(click)
        db.flush()  # token DB-yə yazılsın, sonra email göndərilsin

        success = send_phishing_email(
            to_email=employee.email,
            subject=campaign.template.subject,
            body_html=campaign.template.body_html,
            tracking_url=tracking_url,
        )

        if success:
            sent += 1
        else:
            failed += 1
            logger.warning("Email göndərilmədi: %s", employee.email)

    db.commit()
    logger.info("Kampaniya %s: %d göndərildi, %d uğursuz", campaign_id, sent, failed)
    return {"sent": sent, "failed": failed}
