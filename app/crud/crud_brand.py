from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.brand import Brand
from app.schemas.brand import BrandCreate, BrandUpdate


class CRUDBrand(CRUDBase[Brand, BrandCreate, BrandUpdate]):
    def get_by_owner(self, db: Session, owner_id: int) -> list[Brand]:
        return db.query(Brand).filter(Brand.owner_id == owner_id).all()


crud_brand = CRUDBrand(Brand)
