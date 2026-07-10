from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_current_active_user
from app.crud.crud_application import crud_application
from app.crud.crud_campaign import crud_campaign
from app.db.session import get_db
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationOut, ApplicationUpdate
from app.services.url_verification import verify_submission

router = APIRouter()


@router.post("/", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_campaign(
    application_in: ApplicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    campaign = crud_campaign.get(db, id=application_in.campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    existing = crud_application.get_existing(
        db, user_id=current_user.id, campaign_id=application_in.campaign_id
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this campaign")

    return crud_application.create(db, obj_in=application_in, user_id=current_user.id)


@router.get("/me", response_model=list[ApplicationOut])
def list_my_applications(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)
):
    return crud_application.get_by_user(db, user_id=current_user.id)


@router.get("/campaign/{campaign_id}", response_model=list[ApplicationOut])
def list_applications_for_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    campaign = crud_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view these applications")
    return crud_application.get_by_campaign(db, campaign_id=campaign_id)


@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    application_in: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    application = crud_application.get(db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    is_applicant = application.user_id == current_user.id
    is_brand_owner = application.campaign.brand.owner_id == current_user.id
    if not (is_applicant or is_brand_owner):
        raise HTTPException(status_code=403, detail="Not authorized to update this application")


    update_data = application_in.model_dump(exclude_unset=True)
    if is_applicant and not is_brand_owner:
        update_data.pop("status", None)

    updated = crud_application.update(db, db_obj=application, obj_in=update_data)

    if update_data.get("social_url"):
        updated.submitted_at = datetime.now(timezone.utc)
        updated = verify_submission(updated, campaign_requirements=updated.campaign.description or "")
        db.add(updated)
        db.commit()
        db.refresh(updated)

    return updated


@router.post("/{application_id}/verify", response_model=ApplicationOut)
def verify_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):

    application = crud_application.get(db, id=application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    is_applicant = application.user_id == current_user.id
    is_brand_owner = application.campaign.brand.owner_id == current_user.id
    if not (is_applicant or is_brand_owner):
        raise HTTPException(status_code=403, detail="Not authorized to verify this application")

    application = verify_submission(
        application, campaign_requirements=application.campaign.description or ""
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
