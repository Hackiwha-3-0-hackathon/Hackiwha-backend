from fastapi import APIRouter

from app.api.v1.endpoints import applications, auth, brands, campaigns, profiles, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(brands.router, prefix="/brands", tags=["brands"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(applications.router, prefix="/applications", tags=["applications"])
