import pytest
from app import create_app
from config.config import TestingConfig
from config.db import db
from dao.user_dao import get_user_by_email
from models.user import User

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def register_and_get_token(client, email, password, role='student'):
    """Helper to register and get JWT token"""
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': email,
        'password': password,
        'role': role
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': email,
        'password': password
    })
    return resp.get_json()['token']

def test_register_duplicate(client):
    # first registration
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'dup@example.com',
        'password': 'strongpass',
        'role': 'student'
    })
    # duplicate
    resp = client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'dup@example.com',
        'password': 'another',
        'role': 'student'
    })
    assert resp.status_code == 400
    assert 'error' in resp.get_json()

def test_login_failure(client):
    resp = client.post('/api/v2/auth/login', json={
        'email': 'nosuch@example.com',
        'password': 'doesntmatter'
    })
    assert resp.status_code == 401
    assert 'error' in resp.get_json()

def test_admin_protected_route(client):
    # register admin
    token = register_and_get_token(client, 'admin@example.com', 'adminpass', 'admin')
    # access protected admin route
    resp = client.get('/api/v2/admin/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'total_users' in data

def test_student_cannot_access_admin(client):
    token = register_and_get_token(client, 'student@example.com', 'studentpass', 'student')
    resp = client.get('/api/v2/admin/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 403

def test_instructor_cannot_access_admin(client):
    token = register_and_get_token(client, 'inst@example.com', 'instpass', 'instructor')
    resp = client.get('/api/v2/admin/dashboard', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 403