"""
Phase 2 Integration Tests — Authentication and RBAC.
Tests: registration, login, JWT auth, role authorization.
"""
import pytest


# ─── Helper: register + login, return headers ────────────────────────────────
def _register_user(client, email, password="Secure1234!", full_name="Test User", role="VIEWER"):
    return client.post("/api/v1/auth/register", json={
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": role,
    })


def _login_user(client, email, password="Secure1234!"):
    return client.post("/api/v1/auth/login", data={
        "username": email,
        "password": password,
    })


def _auth_headers(client, email, password="Secure1234!"):
    resp = _login_user(client, email, password)
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ═══════════════════════════════════════════════════════════════════════════════
# 1. REGISTRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestRegistration:
    def test_register_success(self, client):
        resp = _register_user(client, "reg_success@test.com")
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "reg_success@test.com"
        assert body["role"] == "VIEWER"
        assert body["is_active"] is True
        assert "id" in body
        # Must never expose password hash
        assert "hashed_password" not in body
        assert "password" not in body

    def test_register_with_admin_role(self, client):
        resp = _register_user(client, "reg_admin@test.com", role="ADMIN")
        assert resp.status_code == 201
        assert resp.json()["role"] == "ADMIN"

    def test_register_with_ml_engineer_role(self, client):
        resp = _register_user(client, "reg_eng@test.com", role="ML_ENGINEER")
        assert resp.status_code == 201
        assert resp.json()["role"] == "ML_ENGINEER"

    def test_register_duplicate_email_returns_400(self, client):
        _register_user(client, "reg_dup@test.com")
        resp = _register_user(client, "reg_dup@test.com")
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"].lower()

    def test_register_short_password_returns_422(self, client):
        resp = _register_user(client, "reg_short@test.com", password="abc")
        assert resp.status_code == 422

    def test_register_invalid_email_returns_422(self, client):
        resp = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "full_name": "Test",
            "password": "Secure1234!",
        })
        assert resp.status_code == 422

    def test_register_missing_fields_returns_422(self, client):
        resp = client.post("/api/v1/auth/register", json={})
        assert resp.status_code == 422

    def test_register_blank_name_returns_422(self, client):
        resp = _register_user(client, "blankname@test.com", full_name="   ")
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════════════════════════
# 2. LOGIN TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestLogin:
    def test_login_success(self, client):
        _register_user(client, "login_ok@test.com")
        resp = _login_user(client, "login_ok@test.com")
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == "login_ok@test.com"

    def test_login_wrong_password_returns_401(self, client):
        _register_user(client, "login_bad@test.com")
        resp = _login_user(client, "login_bad@test.com", password="WrongPassword!")
        assert resp.status_code == 401
        assert "incorrect" in resp.json()["detail"].lower()

    def test_login_nonexistent_user_returns_401(self, client):
        resp = _login_user(client, "ghost@test.com")
        assert resp.status_code == 401

    def test_login_uses_oauth2_form_format(self, client):
        """Verify that /login accepts form-encoded data (OAuth2 spec)."""
        _register_user(client, "login_form@test.com")
        resp = client.post("/api/v1/auth/login", data={
            "username": "login_form@test.com",
            "password": "Secure1234!",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()


# ═══════════════════════════════════════════════════════════════════════════════
# 3. JWT AUTHENTICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestJWTAuth:
    def test_me_with_valid_token(self, client):
        _register_user(client, "jwt_me@test.com")
        headers = _auth_headers(client, "jwt_me@test.com")
        resp = client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == "jwt_me@test.com"
        assert "hashed_password" not in body

    def test_me_without_token_returns_401(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer obviously.invalid.token"
        })
        assert resp.status_code == 401

    def test_me_with_expired_token_returns_401(self, client):
        """Manually craft an expired token and verify rejection."""
        from backend.app.authentication.jwt import create_access_token
        from datetime import timedelta
        expired_token = create_access_token(
            data={"sub": "jwt_me@test.com"},
            expires_delta=timedelta(seconds=-10),
        )
        resp = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# 4. ROLE-BASED AUTHORIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestRBAC:
    def test_admin_can_list_users(self, client):
        _register_user(client, "rbac_admin@test.com", role="ADMIN")
        headers = _auth_headers(client, "rbac_admin@test.com")
        resp = client.get("/api/v1/users/", headers=headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_viewer_cannot_list_users(self, client):
        _register_user(client, "rbac_viewer@test.com", role="VIEWER")
        headers = _auth_headers(client, "rbac_viewer@test.com")
        resp = client.get("/api/v1/users/", headers=headers)
        assert resp.status_code == 403

    def test_ml_engineer_cannot_list_users(self, client):
        _register_user(client, "rbac_eng@test.com", role="ML_ENGINEER")
        headers = _auth_headers(client, "rbac_eng@test.com")
        resp = client.get("/api/v1/users/", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_update_user_role(self, client):
        # Create viewer, then have admin promote them
        viewer_resp = _register_user(client, "rbac_promote@test.com", role="VIEWER")
        viewer_id = viewer_resp.json()["id"]

        _register_user(client, "rbac_admin2@test.com", role="ADMIN")
        admin_headers = _auth_headers(client, "rbac_admin2@test.com")

        resp = client.patch(
            f"/api/v1/users/{viewer_id}",
            json={"role": "ML_ENGINEER"},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "ML_ENGINEER"

    def test_admin_can_deactivate_user(self, client):
        target_resp = _register_user(client, "rbac_deact@test.com")
        target_id = target_resp.json()["id"]

        _register_user(client, "rbac_admin3@test.com", role="ADMIN")
        admin_headers = _auth_headers(client, "rbac_admin3@test.com")

        resp = client.patch(
            f"/api/v1/users/{target_id}",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False

    def test_viewer_cannot_update_user(self, client):
        _register_user(client, "rbac_viewer2@test.com", role="VIEWER")
        headers = _auth_headers(client, "rbac_viewer2@test.com")
        resp = client.patch(
            "/api/v1/users/1",
            json={"role": "ADMIN"},
            headers=headers,
        )
        assert resp.status_code == 403

    def test_unauthenticated_cannot_access_users(self, client):
        resp = client.get("/api/v1/users/")
        assert resp.status_code == 401

    def test_deactivated_user_cannot_login(self, client):
        # Register a user, deactivate, then try login
        _register_user(client, "rbac_deact2@test.com")
        _register_user(client, "rbac_admin4@test.com", role="ADMIN")
        admin_headers = _auth_headers(client, "rbac_admin4@test.com")

        # Find user id
        users_resp = client.get("/api/v1/users/", headers=admin_headers)
        user_id = None
        for u in users_resp.json():
            if u["email"] == "rbac_deact2@test.com":
                user_id = u["id"]
                break
        assert user_id is not None

        # Deactivate
        client.patch(f"/api/v1/users/{user_id}", json={"is_active": False}, headers=admin_headers)

        # Try login — should fail
        resp = _login_user(client, "rbac_deact2@test.com")
        assert resp.status_code == 401
