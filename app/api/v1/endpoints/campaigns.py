from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.deps import get_current_active_user
from app.crud.crud_brand import crud_brand
from app.crud.crud_campaign import crud_campaign
from app.crud.crud_profile import crud_profile
from app.db.session import get_db
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignOut, CampaignUpdate
from app.services.performance_insights import get_top_performing_submissions
from app.services.recommendations import recommend_campaigns_for_profile

router = APIRouter()


@router.get("/recommended", response_model=list[CampaignOut])
def get_recommended_campaigns(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    profile = crud_profile.get_by_user_id(db, user_id=current_user.id)
    return recommend_campaigns_for_profile(db, profile=profile, limit=limit)


@router.get("/{campaign_id}/insights")
def get_campaign_insights(campaign_id: int, db: Session = Depends(get_db)):
    campaign = crud_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    top_submissions = get_top_performing_submissions(db, campaign_id=campaign_id)

    if not settings.AI_FEATURES_ENABLED:
        return {
            "ai_analysis_enabled": False,
            "message": "AI pattern analysis not enabled yet. Showing raw top performers.",
            "top_submissions": [
                {"application_id": s.id, "current_views": s.current_views, "engagement_rate": s.engagement_rate}
                for s in top_submissions
            ],
        }

    # TODO:  patterns = analyze_viral_patterns(top_submissions) uncomment once implemented
    # return {"ai_analysis_enabled": True, **patterns}
    raise HTTPException(status_code=501, detail="AI pattern analysis not implemented yet.")


@router.get("/", response_model=list[CampaignOut])
def list_campaigns(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = Query(True, description="Only return active campaigns"),
    db: Session = Depends(get_db),
):
    if active_only:
        return crud_campaign.get_active(db, skip=skip, limit=limit)
    return crud_campaign.get_multi(db, skip=skip, limit=limit)


@router.get("/{campaign_id}", response_model=CampaignOut)
def read_campaign(campaign_id: int, db: Session = Depends(get_db)):
    campaign = crud_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.post(
    "/brand/{brand_id}", response_model=CampaignOut, status_code=status.HTTP_201_CREATED
)
def create_campaign(
    brand_id: int,
    campaign_in: CampaignCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    brand = crud_brand.get(db, id=brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    if brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to create campaigns for this brand")
    return crud_campaign.create(db, obj_in=campaign_in, brand_id=brand_id)


@router.get("/brand/{brand_id}", response_model=list[CampaignOut])
def list_campaigns_for_brand(brand_id: int, db: Session = Depends(get_db)):
    return crud_campaign.get_by_brand(db, brand_id=brand_id)


@router.put("/{campaign_id}", response_model=CampaignOut)
def update_campaign(
    campaign_id: int,
    campaign_in: CampaignUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    campaign = crud_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this campaign")
    return crud_campaign.update(db, db_obj=campaign, obj_in=campaign_in)


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    campaign = crud_campaign.get(db, id=campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.brand.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")
    crud_campaign.remove(db, id=campaign_id)
