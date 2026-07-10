import datetime
from pydantic import BaseModel, ConfigDict
from app.models.application import ApplicationStatus, VerificationStatus


class ApplicationBase(BaseModel):
    social_url: str | None = None


class ApplicationCreate(ApplicationBase):
    campaign_id: int


class ApplicationUpdate(BaseModel):
    social_url: str | None = None
    status: ApplicationStatus | None = None

class ApplicationOut(ApplicationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    user_id: int
    status: ApplicationStatus
    applied_at: datetime.datetime
    submitted_at: datetime.datetime | None = None
    verification_status: VerificationStatus
    verification_notes: str | None = None
    current_views: int
    engagement_rate: float | None = None
    amount_paid: float
