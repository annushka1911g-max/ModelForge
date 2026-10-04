"""
Unit tests for application settings and environment loading.
"""
from backend.app.configuration.settings import settings


def test_settings_app_name():
    assert settings.APP_NAME == "ModelForge"


def test_settings_database_url_is_set():
    assert settings.DATABASE_URL is not None
    assert settings.DATABASE_URL.startswith("postgresql://")


def test_settings_api_prefix():
    assert settings.API_V1_STR == "/api/v1"


def test_settings_cors_origins_not_empty():
    assert len(settings.BACKEND_CORS_ORIGINS) > 0


def test_settings_model_cache_max_size():
    assert settings.MODEL_CACHE_MAX_SIZE >= 1
