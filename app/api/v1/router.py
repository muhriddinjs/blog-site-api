from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.articles import public_router as articles_public, admin_router as articles_admin
from app.api.v1.endpoints.portfolios import public_router as portfolios_public, admin_router as portfolios_admin
from app.api.v1.endpoints.certificates import public_router as certificates_public, admin_router as certificates_admin
from app.api.v1.endpoints.about import public_router as about_public, admin_router as about_admin

api_router = APIRouter(prefix="/api/v1")

# Auth
api_router.include_router(auth_router)

# Public
api_router.include_router(articles_public)
api_router.include_router(portfolios_public)
api_router.include_router(certificates_public)
api_router.include_router(about_public)

# Admin
api_router.include_router(articles_admin)
api_router.include_router(portfolios_admin)
api_router.include_router(certificates_admin)
api_router.include_router(about_admin)
