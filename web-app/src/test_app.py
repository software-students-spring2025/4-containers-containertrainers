'''Test App'''

import importlib.util
import sys
import os
from unittest.mock import patch
import pytest
from bson import ObjectId

# Load the app module
app_path = os.path.join(os.path.dirname(__file__), "app.py")
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)

app = app_module.app


@pytest.fixture
def client():
    '''Fixture for Flask test client.'''
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_home_route(client):
    '''Test that the home page loads successfully.'''
    response = client.get("/")
    assert response.status_code == 200

def test_signup_get(client):
    '''Test that the signup page loads successfully on GET request.'''
    response = client.get("/signup")
    assert response.status_code == 200

def test_signup_post_success(client):
    '''Test successful signup with a new username and password.'''
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = client.post("/signup", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_db.insert_one.assert_called_once()

def test_signup_post_existing_user(client):
    '''Test signup with an already existing username.'''
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {"username": "testuser"}
        response = client.post("/signup", data={
            "username": "testuser",
            "password": "testpass"
        })
        html = response.data.decode("utf-8")
        assert "Account with this username already created." in html

def test_signup_post_missing_fields(client):
    '''Test signup with missing username and password fields.'''
    response = client.post("/signup", data={
        "username": "",
        "password": ""
    })
    html = response.data.decode("utf-8")
    assert "All fields are required" in html

def test_login_get(client):
    '''Test that the login page loads successfully on GET request.'''
    response = client.get("/login")
    assert response.status_code == 200

def test_login_post_success(client):
    '''Test successful login with valid credentials.'''
    with patch.object(app_module.db, "accounts") as mock_db, \
         patch("app.check_password_hash", return_value=True):
        mock_user = {
            "_id": ObjectId(),
            "username": "testuser",
            "password": "hashedpass"
        }
        mock_db.find_one.return_value = mock_user
        response = client.post("/login", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=True)
        assert response.status_code == 200

def test_login_post_invalid(client):
    '''Test login attempt with invalid credentials.'''
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = client.post("/login", data={
            "username": "testuser",
            "password": "wrongpass"
        })
        html = response.data.decode("utf-8")
        assert "Invalid username or password" in html

def test_profile_route_authenticated(client):
    '''Test access to profile page for authenticated user.'''
    test_user_id = str(ObjectId())
    with client.session_transaction() as sess:
        sess["user_id"] = test_user_id

    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {"_id": ObjectId(test_user_id), "username": "testuser"}
        response = client.get("/profile")
        assert b"testuser" in response.data

def test_profile_route_not_authenticated(client):
    '''Test redirect to login page when user is not authenticated.'''
    response = client.get("/profile", follow_redirects=True)
    assert b"login" in response.data.lower()

def test_logout_route(client):
    '''Test logout clears session and returns home page.'''
    with client.session_transaction() as sess:
        sess["user_id"] = str(ObjectId())
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200