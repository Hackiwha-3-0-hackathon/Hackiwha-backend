"""
Submission link verification.

Pipeline for a creator-submitted `social_url`:
  1. Reachability check (real, works today) — is the link valid / not broken.
  2. Product-content check (AI, STUBBED)   — does the video actually feature
     the brand's product / campaign requirements.
  3. NSFW check (AI, STUBBED)              — is the content safe to publish
     under a brand's name.

Until steps 2 and 3 are implemented, `verify_submission()` only runs the
reachability check and leaves the application in `pending` verification
status with a note, so a human can review it in the meantime. Once the AI
calls below are wired up, uncomment them and the pipeline becomes fully
automatic.
"""

import httpx

from app.core.config import settings
from app.models.application import Application, VerificationStatus


def is_url_reachable(url: str, timeout: float = 8.0) -> tuple[bool, str]:
    """Real check: does the URL resolve and return a non-error status code."""
    if not url:
        return False, "No URL provided."
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            # Some platforms (TikTok/IG) reject HEAD requests, so try GET.
            response = client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code < 400:
            return True, f"URL reachable ({response.status_code})."
        return False, f"URL returned status {response.status_code}."
    except httpx.RequestError as exc:
        return False, f"URL unreachable: {exc}"


# ---------------------------------------------------------------------------
# AI checks — NOT IMPLEMENTED YET. Wire up your model/provider of choice
# (vision-language model, moderation API, etc.) then uncomment below and
# call them from verify_submission().
# ---------------------------------------------------------------------------

# def detect_product_content(url: str, campaign_requirements: str) -> tuple[bool, str]:
#     """
#     Uses a vision/video-understanding model to confirm the submitted video
#     actually features the brand's product / meets campaign requirements.
#     Returns (passed: bool, reasoning: str).
#     """
#     # Example shape once implemented:
#     # frames = extract_keyframes(url)
#     # result = ai_client.analyze(frames, prompt=f"Does this show: {campaign_requirements}?")
#     # return result.match, result.reasoning
#     raise NotImplementedError


# def detect_nsfw(url: str) -> tuple[bool, str]:
#     """
#     Runs the video/thumbnail through a moderation model.
#     Returns (is_safe: bool, reasoning: str).
#     """
#     # result = moderation_client.classify(url)
#     # return not result.is_nsfw, result.reasoning
#     raise NotImplementedError


def verify_submission(application: Application, campaign_requirements: str = "") -> Application:
    """
    Orchestrates the verification pipeline and mutates the application's
    verification fields in place (caller is responsible for committing).
    """
    if not settings.AI_FEATURES_ENABLED:
        application.verification_status = VerificationStatus.pending
        application.verification_notes = (
            "AI verification is disabled (AI_FEATURES_ENABLED=false). "
            "Only reachability was checked."
        )

    reachable, reachable_note = is_url_reachable(application.social_url or "")
    if not reachable:
        application.verification_status = VerificationStatus.flagged
        application.verification_notes = reachable_note
        return application

    # --- once implemented, replace the block below with the real checks ---
    # content_ok, content_note = detect_product_content(application.social_url, campaign_requirements)
    # nsfw_ok, nsfw_note = detect_nsfw(application.social_url)
    # if content_ok and nsfw_ok:
    #     application.verification_status = VerificationStatus.verified
    #     application.verification_notes = f"{content_note} | {nsfw_note}"
    # else:
    #     application.verification_status = VerificationStatus.flagged
    #     application.verification_notes = f"{content_note} | {nsfw_note}"
    # return application

    application.verification_status = VerificationStatus.pending
    application.verification_notes = f"{reachable_note} Content/NSFW AI checks not yet enabled."
    return application
