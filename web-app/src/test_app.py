# pylint: disable=import-error,redefined-outer-name


"""Test for App"""

import importlib.util
import sys
import os
from io import BytesIO
from unittest.mock import patch
from bson import ObjectId
import pytest

# Load the app module
app_path = os.path.join(os.path.dirname(__file__), "app.py")
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)

app = app_module.app


@pytest.fixture
def test_client():
    """Fixture for Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_home_route(test_client):
    """Test that the home page loads successfully."""
    response = test_client.get("/")
    assert response.status_code == 200


def test_signup_get(test_client):
    """Test that the signup page loads successfully on GET request."""
    response = test_client.get("/signup")
    assert response.status_code == 200


def test_signup_post_success(test_client):
    """Test successful signup with a new username and password."""
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = test_client.post(
            "/signup",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        mock_db.insert_one.assert_called_once()


def test_signup_post_existing_user(test_client):
    """Test signup with an already existing username."""
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {"username": "testuser"}
        response = test_client.post(
            "/signup", data={"username": "testuser", "password": "testpass"}
        )
        html = response.data.decode("utf-8")
        assert "Account with this username already created." in html


def test_signup_post_missing_fields(test_client):
    """Test signup with missing username and password fields."""
    response = test_client.post("/signup", data={"username": "", "password": ""})
    html = response.data.decode("utf-8")
    assert "All fields are required" in html


def test_login_get(test_client):
    """Test that the login page loads successfully on GET request."""
    response = test_client.get("/login")
    assert response.status_code == 200


def test_login_post_success(test_client):
    """Test successful login with valid credentials."""
    with patch.object(app_module.db, "accounts") as mock_db, patch(
        "app.check_password_hash", return_value=True
    ):
        mock_user = {
            "_id": ObjectId(),
            "username": "testuser",
            "password": "hashedpass",
        }
        mock_db.find_one.return_value = mock_user
        response = test_client.post(
            "/login",
            data={"username": "testuser", "password": "testpass"},
            follow_redirects=True,
        )
        assert response.status_code == 200


def test_login_post_invalid(test_client):
    """Test login attempt with invalid credentials."""
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = test_client.post(
            "/login", data={"username": "testuser", "password": "wrongpass"}
        )
        html = response.data.decode("utf-8")
        assert "Invalid username or password" in html


def test_profile_route_authenticated(test_client):
    """Test access to profile page for authenticated user."""
    test_user_id = str(ObjectId())
    with test_client.session_transaction() as sess:
        sess["user_id"] = test_user_id

    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {
            "_id": ObjectId(test_user_id),
            "username": "testuser",
        }
        response = test_client.get("/profile")
        assert b"testuser" in response.data


def test_profile_route_not_authenticated(test_client):
    """Test redirect to login page when user is not authenticated."""
    response = test_client.get("/profile", follow_redirects=True)
    assert b"login" in response.data.lower()


def test_logout_route(test_client):
    """Test logout clears session and returns home page."""
    with test_client.session_transaction() as sess:
        sess["user_id"] = str(ObjectId())
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

def test_record_page(test_client):
    """Test the record route loads successfully."""
    response = test_client.get("/record")
    assert response.status_code == 200
    assert b"<html" in response.data

def test_upload_audio_missing_file(test_client):
    """Test upload without audio field returns failure."""
    response = test_client.post("/upload", data={})
    json_response = response.get_json()

    assert response.status_code == 200
    assert json_response["success"] is False

def test_upload_audio_success(test_client):
    """Test successful audio file upload."""
    dummy_audio = (BytesIO(b"fake audio"), "test_audio.webm")
    data = {"audio": dummy_audio}

    response = test_client.post("/upload", data=data, content_type="multipart/form-data")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["success"] is True
    assert "filename" in json_data
