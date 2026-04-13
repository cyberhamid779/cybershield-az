from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.services.database import get_db
from app.services.auth import get_current_admin
from app.models.campaign import Campaign, CampaignStatus

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    template_id: int


class CampaignOut(BaseModel):
    id: int
    name: str
    template_id: int
    status: CampaignStatus

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CampaignOut])
def list_campaigns(db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    return db.query(Campaign).filter(Campaign.org_id == current_user.org_id).all()


@router.post("/", response_model=CampaignOut)
def create_campaign(data: CampaignCreate, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    campaign = Campaign(org_id=current_user.org_id, name=data.name, template_id=data.template_id)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/launch")
def launch_campaign(campaign_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Tapılmadı")
    if campaign.status != CampaignStatus.draft:
        raise HTTPException(status_code=400, detail="Kampaniya artıq aktiv və ya tamamlanmışdır")
    from app.services.campaign import launch_campaign
    campaign.status = CampaignStatus.active
    db.commit()
    result = launch_campaign(campaign_id, db)
    return {"message": "Kampaniya başladıldı", "sent": result["sent"], "failed": result["failed"]}


@router.get("/{campaign_id}/stats")
def campaign_stats(campaign_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_admin)):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id, Campaign.org_id == current_user.org_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Tapılmadı")
    from app.models.click import Click
    clicks = db.query(Click).filter(Click.campaign_id == campaign_id).all()
    total = len(clicks)
    clicked = sum(1 for c in clicks if c.clicked)
    trained = sum(1 for c in clicks if c.trained)
    return {
        "campaign_id": campaign_id,
        "total_targets": total,
        "clicked": clicked,
        "click_rate": round(clicked / total * 100, 1) if total else 0,
        "trained": trained,
    }
