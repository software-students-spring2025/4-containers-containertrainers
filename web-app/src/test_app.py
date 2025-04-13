# pylint: disable=import-error,redefined-outer-name

"""Test for App"""

import importlib.util
import sys
import os
from io import BytesIO
from unittest.mock import patch, MagicMock
from bson import ObjectId
import pytest

# Append the machine-learning-client folder so that client.py is importable.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../machine-learning-client")))
from client import process_audio  # noqa: E402

# Load the app module from the local file.
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
    response = test_client.get("/")
    assert response.status_code == 200


def test_signup_get(test_client):
    response = test_client.get("/signup")
    assert response.status_code == 200


@patch.object(app_module.db, "accounts")
def test_signup_post_success(mock_accounts, test_client):
    mock_accounts.find_one.return_value = None
    response = test_client.post(
        "/signup", data={"username": "testuser", "password": "testpass"}, follow_redirects=True
    )
    assert response.status_code == 200
    mock_accounts.insert_one.assert_called_once()


@patch.object(app_module.db, "accounts")
def test_signup_post_existing_user(mock_accounts, test_client):
    mock_accounts.find_one.return_value = {"username": "testuser"}
    response = test_client.post(
        "/signup", data={"username": "testuser", "password": "testpass"}
    )
    assert "Account with this username already created." in response.data.decode()


def test_signup_post_missing_fields(test_client):
    response = test_client.post("/signup", data={"username": "", "password": ""})
    assert "All fields are required" in response.data.decode()


def test_login_get(test_client):
    response = test_client.get("/login")
    assert response.status_code == 200


@patch("app.check_password_hash", return_value=True)
@patch.object(app_module.db, "accounts")
def test_login_post_success(mock_accounts, mock_hash, test_client):
    mock_accounts.find_one.return_value = {
        "_id": ObjectId(),
        "username": "testuser",
        "password": "hashedpass",
    }
    response = test_client.post(
        "/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True
    )
    assert response.status_code == 200


@patch.object(app_module.db, "accounts")
def test_login_post_invalid(mock_accounts, test_client):
    mock_accounts.find_one.return_value = None
    response = test_client.post(
        "/login", data={"username": "testuser", "password": "wrongpass"}
    )
    assert "Invalid username or password" in response.data.decode()


@patch.object(app_module.db, "accounts")
def test_profile_route_authenticated(mock_accounts, test_client):
    test_user_id = str(ObjectId())
    with test_client.session_transaction() as sess:
        sess["user_id"] = test_user_id

    mock_accounts.find_one.return_value = {
        "_id": ObjectId(test_user_id),
        "username": "testuser",
    }

    response = test_client.get("/profile")
    assert b"testuser" in response.data


def test_profile_route_not_authenticated(test_client):
    response = test_client.get("/profile", follow_redirects=True)
    assert b"login" in response.data.lower()


def test_logout_route(test_client):
    with test_client.session_transaction() as sess:
        sess["user_id"] = str(ObjectId())
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200


def test_record_page(test_client):
    response = test_client.get("/record")
    assert response.status_code == 200
    assert b"<html" in response.data


@patch.object(app_module.db, "recordings")
def test_upload_audio_missing_file(mock_recordings, test_client):
    response = test_client.post("/upload", data={})
    json_response = response.get_json()
    assert response.status_code == 200
    assert json_response["success"] is False


@patch.object(app_module.db, "recordings")
def test_upload_audio_success(mock_recordings, test_client):
    # Simulate no existing recordings.
    mock_recordings.find.return_value = []  
    dummy_audio = (BytesIO(b"fake audio"), "test_audio.webm")
    data = {"audio": dummy_audio}

    response = test_client.post(
        "/upload", data=data, content_type="multipart/form-data"
    )
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["success"] is True
    assert "filename" in json_data


@patch("app.MongoClient")
@patch("app.process_audio")
def test_get_result(mock_process_audio, mock_mongo_client, test_client):
    # Setup a fake messages collection with a fake document.
    fake_messages_collection = MagicMock()
    fake_messages_collection.find_one.return_value = {
        "transcript": "hello", "summary": "hi"
    }
    # Create a fake db and set up the __getitem__ access.
    fake_db = {"messages": fake_messages_collection}
    fake_speech_db = {"messages": fake_messages_collection}
    # When the app creates a MongoClient and accesses, return our fake db.
    instance = mock_mongo_client.return_value
    instance.__getitem__.return_value = fake_speech_db

    response = test_client.get("/result")
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data["Transcript"] == "hello"
    assert json_data["Summary"] == "hi"
