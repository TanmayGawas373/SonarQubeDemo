import pytest
import json
import os
from app import create_app
from config.config import TestingConfig
from config.db import db
from models.user import User
from models.course import Course
from models.module import Module
from models.material import Material
from werkzeug.security import generate_password_hash
from dao.material_dao import create_material

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

def get_instructor_headers(client):
    """Get instructor authentication headers"""
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'instructor_mat@example.com',
        'password': 'InstPass1',
        'role': 'instructor'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'instructor_mat@example.com',
        'password': 'InstPass1'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def get_student_headers(client):
    """Get student authentication headers"""
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'student_mat@example.com',
        'password': 'StudPass1',
        'role': 'student'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'student_mat@example.com',
        'password': 'StudPass1'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_material_upload_v2(client, app):
    """Test material upload via v2 endpoint"""
    instructor_headers = get_instructor_headers(client)
    
    # Create course and module with instructor_id
    with app.app_context():
        instructor = User.query.filter_by(email='instructor_mat@example.com').first()
        course = Course(title='MatCourse', description='Course with materials', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module 1', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Create a test file with allowed extension (pdf)
    upload_dir = os.path.join('uploads', str(module_id))
    os.makedirs(upload_dir, exist_ok=True)
    test_file_path = os.path.join(upload_dir, 'test.pdf')
    with open(test_file_path, 'wb') as f:
        f.write(b'test content')
    
    try:
        # Upload material
        with open(test_file_path, 'rb') as f:
            upload_resp = client.post(
                f'/api/v2/modules/{module_id}/materials',
                data={'file': (f, 'test.pdf')},
                content_type='multipart/form-data',
                headers=instructor_headers
            )
        
        assert upload_resp.status_code == 201
        data = upload_resp.get_json()
        assert 'id' in data
        assert data['filename'] == 'test.pdf'
        
        # List materials
        list_resp = client.get(f'/api/v2/modules/{module_id}/materials', headers=instructor_headers)
        assert list_resp.status_code == 200
        materials = list_resp.get_json()
        assert len(materials) == 1
        assert materials[0]['filename'] == 'test.pdf'
        
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)
        if os.path.exists(upload_dir):
            # Only remove if empty
            try:
                os.rmdir(upload_dir)
            except OSError:
                pass

def test_material_download_requires_enrollment(client, app):
    """Test that students must be enrolled to download materials"""
    instructor_headers = get_instructor_headers(client)
    student_headers = get_student_headers(client)
    
    # Create course and module
    with app.app_context():
        instructor = User.query.filter_by(email='instructor_mat@example.com').first()
        course = Course(title='MatCourse2', description='Course with materials', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module 2', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Create a test file and material in DB
    upload_dir = os.path.join('uploads', str(module_id))
    os.makedirs(upload_dir, exist_ok=True)
    test_file_path = os.path.join(upload_dir, 'sample.pdf')
    with open(test_file_path, 'wb') as f:
        f.write(b'PDF content')
    
    try:
        # Create material record
        with app.app_context():
            instructor = User.query.filter_by(email='instructor_mat@example.com').first()
            create_material(module_id=module_id, file_path=test_file_path, file_type='pdf', uploaded_by=instructor.id)
        
        # Attempt download without enrollment - should get 403
        resp = client.get(
            f'/api/v2/courses/{course_id}/modules/{module_id}/materials/sample.pdf',
            headers=student_headers
        )
        assert resp.status_code == 403
        
        # Enroll the student
        enroll_resp = client.post(f'/api/v2/courses/{course_id}/enroll', headers=student_headers)
        assert enroll_resp.status_code == 201
        
        # Now download should succeed
        resp = client.get(
            f'/api/v2/courses/{course_id}/modules/{module_id}/materials/sample.pdf',
            headers=student_headers
        )
        assert resp.status_code == 200
        assert resp.data == b'PDF content'
        
    finally:
        # Skip file cleanup on Windows due to file handle issues with send_from_directory
        # The test passes regardless; cleanup would be handled by test environment
        import platform
        if platform.system() != 'Windows':
            import time
            time.sleep(0.1)
            if os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                except (OSError, PermissionError):
                    pass
            if os.path.exists(upload_dir):
                try:
                    os.rmdir(upload_dir)
                except OSError:
                    pass

def test_material_delete_v2(client, app):
    """Test material deletion via v2 endpoint"""
    instructor_headers = get_instructor_headers(client)
    
    # Create course and module
    with app.app_context():
        instructor = User.query.filter_by(email='instructor_mat@example.com').first()
        course = Course(title='DeleteMatCourse', description='Test', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Create a test file and upload
    upload_dir = os.path.join('uploads', str(module_id))
    os.makedirs(upload_dir, exist_ok=True)
    test_file_path = os.path.join(upload_dir, 'delete_me.pdf')
    with open(test_file_path, 'wb') as f:
        f.write(b'delete me')
    
    try:
        with open(test_file_path, 'rb') as f:
            upload_resp = client.post(
                f'/api/v2/modules/{module_id}/materials',
                data={'file': (f, 'delete_me.pdf')},
                content_type='multipart/form-data',
                headers=instructor_headers
            )
        assert upload_resp.status_code == 201
        material_id = upload_resp.get_json()['id']
        
        # Delete material
        del_resp = client.delete(
            f'/api/v2/modules/{module_id}/materials/{material_id}',
            headers=instructor_headers
        )
        assert del_resp.status_code == 200
        
        # Verify deleted
        list_resp = client.get(f'/api/v2/modules/{module_id}/materials', headers=instructor_headers)
        assert list_resp.status_code == 200
        assert len(list_resp.get_json()) == 0
        
    finally:
        # Skip file cleanup on Windows due to file handle issues with send_from_directory
        # The test passes regardless; cleanup would be handled by test environment
        import platform
        if platform.system() != 'Windows':
            import time
            time.sleep(0.1)
            if os.path.exists(test_file_path):
                try:
                    os.remove(test_file_path)
                except (OSError, PermissionError):
                    pass
            if os.path.exists(upload_dir):
                try:
                    os.rmdir(upload_dir)
                except OSError:
                    pass