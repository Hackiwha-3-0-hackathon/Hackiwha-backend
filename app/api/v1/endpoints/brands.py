from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user
from app.crud.crud_brand import crud_brand
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandOut, BrandUpdate

router = APIRouter()


@router.post("/", response_model=BrandOut, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud_brand.create(db, obj_in=brand_in, owner_id=current_user.id)


@router.get("/", response_model=list[BrandOut])
def list_brands(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_brand.get_multi(db, skip=skip, limit=limit)


@router.get("/me", response_model=list[BrandOut])
def list_my_brands(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return crud_brand.get_by_owner(db, owner_id=current_user.id)


@router.get("/{brand_id}", response_model=BrandOut)
def read_brand(brand_id: int, db: Session = Depends(get_db)):
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: int,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this brand")
    return crud_brand.update(db, db_obj=brand, obj_in=brand_in)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this brand")
    crud_brand.remove(db, id=brand_id)
