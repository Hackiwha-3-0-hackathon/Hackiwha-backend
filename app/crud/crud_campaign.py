from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.campaign import Campaign, CampaignStatus
from app.schemas.campaign import CampaignCreate, CampaignUpdate


class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
    def get_by_brand(self, db: Session, brand_id: int) -> list[Campaign]:
        return db.query(Campaign).filter(Campaign.brand_id == brand_id).all()

    def get_active(self, db: Session, skip: int = 0, limit: int = 100) -> list[Campaign]:
        return (
            db.query(Campaign)
            .filter(Campaign.status == CampaignStatus.active)
            .offset(skip)
            .limit(limit)
            .all()
        )


crud_campaign = CRUDCampaign(Campaign)
