from fastapi import APIRouter
from app.api.routes import (
    auth, gazette, portal, desk, clearance, members, dashboards, reports, users, audit, settings
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(gazette.router)
api_router.include_router(portal.router)
api_router.include_router(desk.router)
api_router.include_router(clearance.router)
api_router.include_router(members.router)
api_router.include_router(dashboards.router)
api_router.include_router(reports.router)
api_router.include_router(users.router)
api_router.include_router(audit.router)
api_router.include_router(settings.router)
