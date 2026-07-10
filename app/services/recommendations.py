import re
from collections import Counter

from sqlalchemy.orm import Session

from app.crud.crud_campaign import crud_campaign
from app.models.campaign import Campaign
from app.models.profile import Profile

_STOPWORDS = {
    "the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "with",
    "your", "you", "is", "are", "be", "this", "that", "our", "we", "it",
}


def _tokenize(text: str | None) -> Counter:
    if not text:
        return Counter()
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    return Counter(w for w in words if w not in _STOPWORDS)


def recommend_campaigns_for_profile(
    db: Session, profile: Profile | None, limit: int = 10
) -> list[Campaign]:
    active_campaigns = crud_campaign.get_active(db, skip=0, limit=200)

    if not profile or not (profile.bio or profile.portfolio_url):
        return active_campaigns[:limit]

    profile_tokens = _tokenize(profile.bio) + _tokenize(profile.portfolio_url)
    if not profile_tokens:
        return active_campaigns[:limit]

    scored: list[tuple[int, Campaign]] = []
    for campaign in active_campaigns:
        campaign_tokens = _tokenize(campaign.title) + _tokenize(campaign.description)
        overlap = sum((profile_tokens & campaign_tokens).values())
        scored.append((overlap, campaign))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [campaign for _, campaign in scored[:limit]]


#TODO: implementing embeddings-based similarity (semantic, not just keyword).

# from app.core.config import settings
#
# def embed(text: str) -> list[float]:
#     raise NotImplementedError
# def recommend_campaigns_semantic(
#     db: Session, profile: Profile | None, limit: int = 10
# ) -> list[Campaign]:
#     if not settings.AI_FEATURES_ENABLED or not profile:
#         return recommend_campaigns_for_profile(db, profile, limit)
#     profile_vec = embed(f"{profile.bio or ''} {profile.portfolio_url or ''}")
#     active_campaigns = crud_campaign.get_active(db, skip=0, limit=200)
#     scored = [
#         (cosine_similarity(profile_vec, embed(f"{c.title} {c.description or ''}")), c)
#         for c in active_campaigns
#     ]
#     scored.sort(key=lambda pair: pair[0], reverse=True)
#     return [c for _, c in scored[:limit]]
