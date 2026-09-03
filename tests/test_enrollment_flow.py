import pytest
import json
from app import create_app
from config.config import TestingConfig
from config.db import db
from models.user import User
from models.course import Course
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        # Create an admin user
        admin = User(
            email="admin@example.com",
            password_hash=generate_password_hash("AdminPass1"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_admin_headers(client):
    """Get admin authentication headers"""
    resp = client.post('/api/v2/auth/login', json={
        'email': 'admin@example.com',
        'password': 'AdminPass1'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def get_student_headers(client):
    """Get student authentication headers"""
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'student@example.com',
        'password': 'StudPass1',
        'role': 'student'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'student@example.com',
        'password': 'StudPass1'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_enrollment_flow_v2(client):
    """Test enrollment flow using v2 endpoints"""
    admin_headers = get_admin_headers(client)
    student_headers = get_student_headers(client)
    
    # Create a course via admin with instructor_id
    create_resp = client.post(
        '/api/v2/courses',
        data=json.dumps({'title': 'EnrollCourse', 'description': 'Test course', 'instructor_id': 1}),
        content_type="application/json",
        headers=admin_headers
    )
    assert create_resp.status_code == 201
    course_id = json.loads(create_resp.data)['id']
    
    # Student enrolls
    enroll_resp = client.post(
        f'/api/v2/courses/{course_id}/enroll',
        headers=student_headers
    )
    assert enroll_resp.status_code == 201
    assert enroll_resp.get_json()['message'] == 'Enrolled successfully'
    
    # Verify enrollment appears in my enrollments
    resp = client.get('/api/v2/my/enrollments', headers=student_headers)
    assert resp.status_code == 200
    enrollments = resp.get_json()
    assert any(e['course_id'] == course_id for e in enrollments)
    
    # Verify enrollment appears in course enrollments (admin view)
    resp = client.get(f'/api/v2/courses/{course_id}/enrollments', headers=admin_headers)
    assert resp.status_code == 200
    course_enrollments = resp.get_json()
    assert any(e['user_id'] is not None for e in course_enrollments)
    
    # Unenroll
    unenroll_resp = client.delete(f'/api/v2/courses/{course_id}/enroll', headers=student_headers)
    assert unenroll_resp.status_code == 200
    assert unenroll_resp.get_json()['message'] == 'Unenrolled successfully'
    
    # Verify removed from my enrollments
    resp = client.get('/api/v2/my/enrollments', headers=student_headers)
    assert resp.status_code == 200
    enrollments = resp.get_json()
    assert not any(e['course_id'] == course_id for e in enrollments)

def test_enrollment_requires_student_role(client):
    """Test that only students can enroll"""
    admin_headers = get_admin_headers(client)
    
    # Create a course
    create_resp = client.post(
        '/api/v2/courses',
        data=json.dumps({'title': 'Test Course', 'description': 'Test', 'instructor_id': 1}),
        content_type="application/json",
        headers=admin_headers
    )
    course_id = json.loads(create_resp.data)['id']
    
    # Admin tries to enroll (should fail)
    enroll_resp = client.post(f'/api/v2/courses/{course_id}/enroll', headers=admin_headers)
    assert enroll_resp.status_code == 403

def test_enroll_nonexistent_course(client):
    """Test enrolling in non-existent course"""
    student_headers = get_student_headers(client)
    
    resp = client.post('/api/v2/courses/99999/enroll', headers=student_headers)
    # 400 if course not found, 403 if permission issue
    assert resp.status_code in (400, 403)
    assert 'error' in resp.get_json()