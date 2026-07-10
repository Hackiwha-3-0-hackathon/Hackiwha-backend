import datetime

from pydantic import BaseModel, ConfigDict

from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    title: str
    description: str | None = None
    platform: str | None = None
    reward: float
    target_views: int
    total_budget: float | None = None
    deadline: datetime.date | None = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    platform: str | None = None
    reward: float | None = None
    target_views: int | None = None
    total_budget: float | None = None
    deadline: datetime.date | None = None
    status: CampaignStatus | None = None


class CampaignOut(CampaignBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    status: CampaignStatus
    created_at: datetime.datetime
