from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus


def get_top_performing_submissions(
    db: Session, campaign_id: int | None = None, limit: int = 20
) -> list[Application]:
    query = db.query(Application).filter(Application.status == ApplicationStatus.completed)
    if campaign_id is not None:
        query = query.filter(Application.campaign_id == campaign_id)
    return query.order_by(Application.current_views.desc()).limit(limit).all()


#TODO: AI video/pattern analysis to wire here

# from app.core.config import settings
#
# def analyze_viral_patterns(submissions: list[Application]) -> dict:
#  
#     if not settings.AI_FEATURES_ENABLED:
#         raise RuntimeError("AI features are disabled (AI_FEATURES_ENABLED=false).")
#     # transcripts = [transcribe(s.social_url) for s in submissions]
#     # hooks = [extract_hook(t) for t in transcripts]
#     # patterns = ai_client.summarize_patterns(hooks, ...)
#     # return patterns
#     raise NotImplementedError
