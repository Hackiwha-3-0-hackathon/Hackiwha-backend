from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.application import Application
from app.schemas.application import ApplicationCreate, ApplicationUpdate


class CRUDApplication(CRUDBase[Application, ApplicationCreate, ApplicationUpdate]):
    def get_by_user(self, db: Session, user_id: int) -> list[Application]:
        return db.query(Application).filter(Application.user_id == user_id).all()

    def get_by_campaign(self, db: Session, campaign_id: int) -> list[Application]:
        return db.query(Application).filter(Application.campaign_id == campaign_id).all()

    def get_existing(self, db: Session, user_id: int, campaign_id: int) -> Application | None:
        return (
            db.query(Application)
            .filter(Application.user_id == user_id, Application.campaign_id == campaign_id)
            .first()
        )


crud_application = CRUDApplication(Application)
