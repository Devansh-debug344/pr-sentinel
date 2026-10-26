from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.modules.analysis.router import router as analysis_router
from app.modules.ci.router import router as ci_router
from app.modules.investigations.router import router as investigations_router
from app.modules.pull_requests.router import router as pull_requests_router
from app.modules.repositories.router import router as repositories_router
from app.modules.webhooks.router import router as webhooks_router
from app.patches.router import router as patches_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(webhooks_router)
api_router.include_router(repositories_router)
api_router.include_router(pull_requests_router)
api_router.include_router(investigations_router)
api_router.include_router(analysis_router)
api_router.include_router(ci_router)
api_router.include_router(patches_router)

__all__ = ["api_router"]
