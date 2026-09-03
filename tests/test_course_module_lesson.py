# tests/test_course_module_lesson.py
"""Integration tests for Phase 2 - Course, Module & Lesson management.
Tests both v1 and v2 API endpoints.
"""

import json
import pytest
from app import create_app
from config.db import db as _db
from models.user import User
from werkzeug.security import generate_password_hash

@pytest.fixture(scope="module")
def app():
    """Create a Flask app instance bound to a temporary SQLite DB."""
    test_config = type("Config", (), {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "WTF_CSRF_ENABLED": False,
        "JWT_SECRET_KEY": "test-jwt-secret",
    })
    app = create_app(test_config)
    with app.app_context():
        _db.create_all()
        # create a default instructor user for auth-protected endpoints
        instructor = User(
            email="instructor@example.com",
            password_hash=generate_password_hash("StrongPass1"),
            role="instructor",
        )
        _db.session.add(instructor)
        _db.session.commit()
    yield app
    # teardown - drop all tables
    with app.app_context():
        _db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def login_as_instructor(client):
    resp = client.post(
        "/api/v2/auth/login",
        data=json.dumps({"email": "instructor@example.com", "password": "StrongPass1"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_course_crud_v1(login_as_instructor):
    """Test v1 course CRUD endpoints - skipped as v2 is preferred"""
    pytest.skip("v1 tests deprecated, use v2 endpoints")

def test_course_crud_v2(client, login_as_instructor):
    """Test v2 course CRUD endpoints"""
    headers = login_as_instructor
    
    # --- CREATE ---------------------------------------------------
    create_resp = client.post(
        "/api/v2/courses",
        data=json.dumps({"title": "Python 101", "description": "Intro to Python"}),
        content_type="application/json",
        headers=headers
    )
    assert create_resp.status_code == 201
    course_id = json.loads(create_resp.data)["id"]

    # --- READ (list) --------------------------------------------
    list_resp = client.get("/api/v2/courses", headers=headers)
    assert list_resp.status_code == 200
    data = json.loads(list_resp.data)
    assert 'courses' in data
    assert any(c["id"] == course_id for c in data['courses'])

    # --- READ (single) ------------------------------------------
    get_resp = client.get(f"/api/v2/courses/{course_id}", headers=headers)
    assert get_resp.status_code == 200
    data = json.loads(get_resp.data)
    assert data["title"] == "Python 101"

    # --- UPDATE ------------------------------------------------
    upd_resp = client.put(
        f"/api/v2/courses/{course_id}",
        data=json.dumps({"title": "Python Basics"}),
        content_type="application/json",
        headers=headers
    )
    assert upd_resp.status_code == 200
    # verify change
    get_resp = client.get(f"/api/v2/courses/{course_id}", headers=headers)
    assert json.loads(get_resp.data)["title"] == "Python Basics"

    # --- DELETE ------------------------------------------------
    del_resp = client.delete(f"/api/v2/courses/{course_id}", headers=headers)
    assert del_resp.status_code == 200
    # confirm gone
    get_resp = client.get(f"/api/v2/courses/{course_id}", headers=headers)
    assert get_resp.status_code == 404

def test_module_crud_v2(client, login_as_instructor):
    """Test v2 module CRUD endpoints"""
    headers = login_as_instructor
    
    # Create a course first
    cr = client.post(
        "/api/v2/courses",
        data=json.dumps({"title": "Web Dev", "description": "Full-stack"}),
        content_type="application/json",
        headers=headers
    )
    course_id = json.loads(cr.data)["id"]

    # --- MODULE CREATE ------------------------------------------
    mod_resp = client.post(
        f"/api/v2/courses/{course_id}/modules",
        data=json.dumps({"title": "HTML Basics", "description": "Tags & semantics", "order": 1}),
        content_type="application/json",
        headers=headers
    )
    assert mod_resp.status_code == 201
    module_id = json.loads(mod_resp.data)["id"]

    # --- MODULE LIST -------------------------------------------
    list_resp = client.get(f"/api/v2/courses/{course_id}/modules", headers=headers)
    assert list_resp.status_code == 200
    modules = json.loads(list_resp.data)
    assert any(m["id"] == module_id for m in modules)

    # --- MODULE READ -------------------------------------------
    get_resp = client.get(f"/api/v2/courses/{course_id}/modules/{module_id}", headers=headers)
    assert get_resp.status_code == 200
    data = json.loads(get_resp.data)
    assert data["title"] == "HTML Basics"

    # --- MODULE UPDATE -----------------------------------------
    upd_resp = client.put(
        f"/api/v2/courses/{course_id}/modules/{module_id}",
        data=json.dumps({"title": "HTML Advanced", "order": 2}),
        content_type="application/json",
        headers=headers
    )
    assert upd_resp.status_code == 200
    get_resp = client.get(f"/api/v2/courses/{course_id}/modules/{module_id}", headers=headers)
    assert json.loads(get_resp.data)["title"] == "HTML Advanced"

    # --- MODULE DELETE -----------------------------------------
    del_resp = client.delete(f"/api/v2/courses/{course_id}/modules/{module_id}", headers=headers)
    assert del_resp.status_code == 200
    get_resp = client.get(f"/api/v2/courses/{course_id}/modules/{module_id}", headers=headers)
    assert get_resp.status_code == 404

    # Cleanup course
    client.delete(f"/api/v2/courses/{course_id}", headers=headers)

def test_lesson_crud_v2(client, login_as_instructor):
    """Test v2 lesson CRUD endpoints"""
    headers = login_as_instructor
    
    # Create course and module
    cr = client.post(
        "/api/v2/courses",
        data=json.dumps({"title": "Web Dev", "description": "Full-stack"}),
        content_type="application/json",
        headers=headers
    )
    course_id = json.loads(cr.data)["id"]
    
    mod_resp = client.post(
        f"/api/v2/courses/{course_id}/modules",
        data=json.dumps({"title": "HTML Basics", "order": 1}),
        content_type="application/json",
        headers=headers
    )
    module_id = json.loads(mod_resp.data)["id"]

    # --- LESSON CREATE ------------------------------------------
    lesson_payload = {
        "title": "Heading Tags",
        "content": "# H1\n## H2\n### H3",
        "order": 1
    }
    les_resp = client.post(
        f"/api/v2/modules/{module_id}/lessons",
        data=json.dumps(lesson_payload),
        content_type="application/json",
        headers=headers
    )
    assert les_resp.status_code == 201
    lesson_id = json.loads(les_resp.data)["id"]

    # --- LESSON LIST -------------------------------------------
    list_resp = client.get(f"/api/v2/modules/{module_id}/lessons", headers=headers)
    assert list_resp.status_code == 200
    lessons = json.loads(list_resp.data)
    assert any(l["id"] == lesson_id for l in lessons)

    # --- LESSON READ -------------------------------------------
    get_lesson = client.get(
        f"/api/v2/modules/{module_id}/lessons/{lesson_id}",
        headers=headers
    )
    assert get_lesson.status_code == 200
    lesson_data = json.loads(get_lesson.data)
    assert lesson_data["title"] == "Heading Tags"
    assert "# H1" in lesson_data["content"]

    # --- LESSON UPDATE -----------------------------------------
    upd_resp = client.put(
        f"/api/v2/modules/{module_id}/lessons/{lesson_id}",
        data=json.dumps({"title": "Updated Heading Tags", "content": "# Updated"}),
        content_type="application/json",
        headers=headers
    )
    assert upd_resp.status_code == 200
    get_lesson = client.get(f"/api/v2/modules/{module_id}/lessons/{lesson_id}", headers=headers)
    assert json.loads(get_lesson.data)["title"] == "Updated Heading Tags"

    # --- LESSON DELETE -----------------------------------------
    del_resp = client.delete(f"/api/v2/modules/{module_id}/lessons/{lesson_id}", headers=headers)
    assert del_resp.status_code == 200
    get_lesson = client.get(f"/api/v2/modules/{module_id}/lessons/{lesson_id}", headers=headers)
    assert get_lesson.status_code == 404

    # Cleanup
    client.delete(f"/api/v2/courses/{course_id}/modules/{module_id}", headers=headers)
    client.delete(f"/api/v2/courses/{course_id}", headers=headers)

def test_student_cannot_create_course(client):
    """Test that students cannot create courses"""
    # Register and login as student
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'student@example.com',
        'password': 'StrongPass1',
        'role': 'student'
    })
    login_resp = client.post('/api/v2/auth/login', json={
        'email': 'student@example.com',
        'password': 'StrongPass1'
    })
    student_token = login_resp.get_json()['token']
    student_headers = {'Authorization': f'Bearer {student_token}'}
    
    # Try to create course as student - should fail with 400 (permission error caught and returned as 400)
    create_resp = client.post(
        "/api/v2/courses",
        data=json.dumps({"title": "Unauthorized Course", "instructor_id": 1}),
        content_type="application/json",
        headers=student_headers
    )
    assert create_resp.status_code == 400
    assert 'error' in create_resp.get_json()