from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


class CRUDProfile(CRUDBase[Profile, ProfileCreate, ProfileUpdate]):
    def get_by_user_id(self, db: Session, user_id: int) -> Profile | None:
        return db.query(Profile).filter(Profile.user_id == user_id).first()


crud_profile = CRUDProfile(Profile)
