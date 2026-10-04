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
from backend.app.routes.audit_routes import router as audit_router
from backend.app.routes.api_key_routes import router as api_key_router
from backend.app.routes.experiment_routes import router as experiment_router
from backend.app.routes.notification_routes import router as notification_router
from backend.app.routes.search_routes import router as search_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user_router, prefix="/users", tags=["Users (Admin)"])
api_router.include_router(model_router, prefix="/models", tags=["Model Registry"])
api_router.include_router(deployment_router, prefix="/deployments", tags=["Deployments"])
api_router.include_router(inference_router, prefix="/deployments", tags=["Inference"])
api_router.include_router(batch_router, prefix="/batch", tags=["Batch Inference"])
api_router.include_router(monitoring_router, prefix="/monitoring", tags=["Monitoring & Health"])
api_router.include_router(audit_router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(api_key_router, prefix="/api-keys", tags=["API Keys"])
api_router.include_router(experiment_router, prefix="/experiments", tags=["Experiments"])
api_router.include_router(notification_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(search_router, prefix="/search", tags=["Global Search"])
