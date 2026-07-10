import datetime
from pydantic import BaseModel, ConfigDict


class BrandBase(BaseModel):
    company_name: str
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    company_name: str | None = None
    description: str | None = None
    website: str | None = None
    logo_url: str | None = None


class BrandOut(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime.datetime
