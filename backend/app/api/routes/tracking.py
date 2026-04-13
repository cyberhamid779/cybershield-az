import hashlib
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.models.click import Click
from app.models.user import User
from app.models.campaign import Campaign
from app.services.database import get_db
from app.services.email import send_training_email

router = APIRouter()

ALREADY_CLICKED_HTML = """
<html><body style="font-family:sans-serif;text-align:center;padding:60px">
<h2>Bu link artıq qeydə alınmışdır.</h2>
</body></html>
"""


@router.get("/{token}", response_class=HTMLResponse)
def track_click(token: str, request: Request, db: Session = Depends(get_db)):
    click = db.query(Click).filter(Click.token == token).first()

    if not click:
        return HTMLResponse(content="<html><body>Səhifə tapılmadı.</body></html>", status_code=404)

    if click.clicked:
        return HTMLResponse(content=ALREADY_CLICKED_HTML)

    # Klik qeydiyyatı
    ip = request.client.host if request.client else "unknown"
    click.clicked = True
    click.clicked_at = datetime.now(timezone.utc)
    click.ip_hash = hashlib.sha256(ip.encode()).hexdigest()
    db.commit()

    # Təlim emaili göndər
    user = db.query(User).filter(User.id == click.user_id).first()
    campaign = db.query(Campaign).filter(Campaign.id == click.campaign_id).first()
    if user and campaign and campaign.template:
        send_training_email(user.email, user.name, campaign.template.training_html)
        click.trained = True
        db.commit()

    # Təlim səhifəsini göstər
    training_page = campaign.template.training_html if campaign and campaign.template else ""
    return HTMLResponse(content=training_page.replace("{{NAME}}", user.name if user else ""))
