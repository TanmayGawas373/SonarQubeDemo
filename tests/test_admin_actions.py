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
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_admin_headers(client):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'adminx@example.com',
        'password': 'Pass1234',
        'role': 'admin'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'adminx@example.com',
        'password': 'Pass1234'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def get_instructor_headers(client):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'instructor_admin@example.com',
        'password': 'Pass1234',
        'role': 'instructor'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'instructor_admin@example.com',
        'password': 'Pass1234'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_admin_user_management_v2(client, app):
    """Test admin user management via v2 endpoints"""
    admin_headers = get_admin_headers(client)
    
    # Create a normal user directly in DB
    with app.app_context():
        user = User(email='normal@example.com', password_hash='hashed', role='student')
        db.session.add(user)
        db.session.commit()
        user_id = user.id
    
    # List users via admin endpoint
    resp = client.get('/api/v2/admin/users', headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'users' in data
    assert any(u['email'] == 'normal@example.com' for u in data['users'])
    
    # Get single user
    resp = client.get(f'/api/v2/admin/users/{user_id}', headers=admin_headers)
    assert resp.status_code == 200
    user_data = resp.get_json()
    assert user_data['email'] == 'normal@example.com'
    
    # Update user via admin endpoint
    upd_resp = client.put(
        f'/api/v2/admin/users/{user_id}',
        data=json.dumps({'email': 'updated@example.com', 'role': 'instructor'}),
        content_type="application/json",
        headers=admin_headers
    )
    assert upd_resp.status_code == 200
    assert upd_resp.get_json()['role'] == 'instructor'
    
    # Delete user via admin endpoint
    del_resp = client.delete(f'/api/v2/admin/users/{user_id}', headers=admin_headers)
    assert del_resp.status_code == 200
    
    # Verify removal
    resp = client.get('/api/v2/admin/users', headers=admin_headers)
    assert resp.status_code == 200
    users = resp.get_json()['users']
    assert not any(u['id'] == user_id for u in users)

def test_admin_user_management_requires_admin(client, app):
    """Test that instructor cannot access admin user management"""
    instructor_headers = get_instructor_headers(client)
    
    resp = client.get('/api/v2/admin/users', headers=instructor_headers)
    assert resp.status_code == 403

def test_admin_course_management_v2(client, app):
    """Test admin course management via v2 endpoints"""
    admin_headers = get_admin_headers(client)
    
    # Create an instructor user (unique email to avoid conflict)
    with app.app_context():
        instructor = User(email='admin_test_instructor@example.com', password_hash='hashed', role='instructor')
        db.session.add(instructor)
        db.session.commit()
        instructor_id = instructor.id
    
    # Create course as admin with instructor_id
    course_resp = client.post(
        '/api/v2/courses',
        data=json.dumps({'title': 'Instructor Course', 'description': 'Created by instructor', 'instructor_id': instructor_id}),
        content_type="application/json",
        headers=admin_headers
    )
    course_id = json.loads(course_resp.data)['id']
    
    # Admin lists courses
    resp = client.get('/api/v2/admin/courses', headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'courses' in data
    assert any(c['id'] == course_id for c in data['courses'])
    
    # Admin gets single course
    resp = client.get(f'/api/v2/admin/courses/{course_id}', headers=admin_headers)
    assert resp.status_code == 200
    assert resp.get_json()['title'] == 'Instructor Course'
    
    # Admin updates course (without instructor_id - should preserve existing)
    upd_resp = client.put(
        f'/api/v2/admin/courses/{course_id}',
        data=json.dumps({'title': 'Updated by Admin', 'description': 'Admin updated'}),
        content_type="application/json",
        headers=admin_headers
    )
    assert upd_resp.status_code == 200
    
    # Verify update
    resp = client.get(f'/api/v2/admin/courses/{course_id}', headers=admin_headers)
    assert resp.get_json()['title'] == 'Updated by Admin'
    
    # Admin deletes course
    del_resp = client.delete(f'/api/v2/admin/courses/{course_id}', headers=admin_headers)
    assert del_resp.status_code == 200
    
    # Verify deleted
    resp = client.get(f'/api/v2/admin/courses/{course_id}', headers=admin_headers)
    assert resp.status_code == 404

def test_admin_dashboard_v2(client, app):
    """Test admin dashboard via v2 endpoint"""
    admin_headers = get_admin_headers(client)
    
    # Create some test data
    with app.app_context():
        # Add a student
        student = User(email='dash_student@example.com', password_hash='hash', role='student')
        db.session.add(student)
        db.session.commit()
        
        # Add an instructor
        instructor = User(email='dash_inst@example.com', password_hash='hash', role='instructor')
        db.session.add(instructor)
        db.session.commit()
        
        # Add a course
        course = Course(title='Dashboard Course', description='', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
    
    resp = client.get('/api/v2/admin/dashboard', headers=admin_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    
    assert 'total_users' in data
    assert data['total_users'] >= 3  # admin + student + instructor
    assert 'course_count' in data
    assert data['course_count'] >= 1
    assert 'user_distribution' in data
    assert 'popular_courses' in data
    assert 'quiz_analytics' in data