"""
API v1 Router registry.
"""
from fastapi import APIRouter
from backend.app.routes.auth_routes import router as auth_router
from backend.app.routes.user_routes import router as user_router
from backend.app.routes.model_routes import router as model_router
from backend.app.routes.deployment_routes import router as deployment_router
from backend.app.routes.inference_routes import router as inference_router
from backend.app.routes.batch_routes import router as batch_router
from backend.app.routes.monitoring_routes import router as monitoring_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user_router, prefix="/users", tags=["Users (Admin)"])
api_router.include_router(model_router, prefix="/models", tags=["Model Registry"])
api_router.include_router(deployment_router, prefix="/deployments", tags=["Deployments"])
api_router.include_router(inference_router, prefix="/deployments", tags=["Inference"])
api_router.include_router(batch_router, prefix="/batch", tags=["Batch Inference"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring & Health"])
