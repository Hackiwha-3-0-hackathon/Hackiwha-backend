from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user
from app.crud.crud_profile import crud_profile
from app.db.session import get_db
from app.models.user import User
from app.schemas.profile import ProfileCreate, ProfileOut, ProfileUpdate

router = APIRouter()


@router.get("/me", response_model=ProfileOut)
def read_my_profile(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    profile = crud_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.post("/me", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
def create_my_profile(
    profile_in: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    existing = crud_profile.get_by_user_id(db, user_id=current_user.id)
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")
    return crud_profile.create(db, obj_in=profile_in, user_id=current_user.id)


@router.put("/me", response_model=ProfileOut)
def update_my_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = crud_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return crud_profile.update(db, db_obj=profile, obj_in=profile_in)


@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    profile = crud_profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile
