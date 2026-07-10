from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    bio: str | None = None
    portfolio_url: str | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileOut(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
