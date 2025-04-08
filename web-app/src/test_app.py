"""Test App"""

import importlib.util
import sys
import os
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

app_path = os.path.join(os.path.dirname(__file__), "app.py")
spec = importlib.util.spec_from_file_location("app", app_path)
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)

app = app_module.app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

 '''Test that the home page loads successfully.'''
def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200

'''Test that the signup page loads successfully.'''
def test_signup_get(client):
    response = client.get("/signup")
    assert response.status_code == 200

'''Tests successful signup.'''
def test_signup_post_success(client):
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = client.post("/signup", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=True)
        assert response.status_code == 200
        mock_db.insert_one.assert_called_once()
    
'''Tests signup with a username that is already in database.'''
def test_signup_post_existing_user(client):
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {"username": "testuser"}
        response = client.post("/signup", data={
            "username": "testuser",
            "password": "testpass"
        })
        html = response.data.decode("utf-8")
        assert "Account with this username already created." in html
    
'''Test signup with missing username and password fields.'''
def test_signup_post_missing_fields(client):
    response = client.post("/signup", data={
        "username": "",
        "password": ""
    })
    html = response.data.decode("utf-8")
    assert "All fields are required" in html

'''Test that the login page loads successfully on GET request.'''
def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200

'''Test successful login with valid username and password.'''
def test_login_post_success(client):
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

'''Test login attempt with invalid credentials.'''
def test_login_post_invalid(client):
    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = None
        response = client.post("/login", data={
            "username": "testuser",
            "password": "wrongpass"
        })
        html = response.data.decode("utf-8")
        assert "Invalid username or password" in html

'''Tests that the profile page loads when the user is logged in.'''
def test_profile_route_authenticated(client):
    test_user_id = str(ObjectId())
    with client.session_transaction() as sess:
        sess["user_id"] = test_user_id

    with patch.object(app_module.db, "accounts") as mock_db:
        mock_db.find_one.return_value = {"_id": ObjectId(test_user_id), "username": "testuser"}
        response = client.get("/profile")
        assert b"testuser" in response.data
    
'''Tests that unauthenticated access to profile redirects to login page.'''
def test_profile_route_not_authenticated(client):
    response = client.get("/profile", follow_redirects=True)
    assert b"login" in response.data.lower()
   
'''Tests that logout redirects properly.'''
def test_logout_route(client):
    with client.session_transaction() as sess:
        sess["user_id"] = str(ObjectId())
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
