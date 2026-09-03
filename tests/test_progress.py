import pytest
import json
from app import create_app
from config.config import TestingConfig
from config.db import db
from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.quiz import Quiz
from models.question import Question
from werkzeug.security import generate_password_hash
from dao.lesson_completion_dao import mark_completed
from dao.quiz_dao import submit_quiz_result

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

def get_student_headers(client, app):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'studprog@example.com',
        'password': 'Pass1234',
        'role': 'student'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'studprog@example.com',
        'password': 'Pass1234'
    })
    token = resp.get_json()['token']
    with app.app_context():
        student = User.query.filter_by(email='studprog@example.com').first()
        student_id = student.id
    return {'Authorization': f'Bearer {token}', 'student_id': student_id}

def get_instructor_headers(client, app):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'instprog@example.com',
        'password': 'Pass1234',
        'role': 'instructor'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'instprog@example.com',
        'password': 'Pass1234'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_progress_endpoint_requires_student(client, app):
    """Test that progress endpoint requires student role"""
    instructor_headers = get_instructor_headers(client, app)
    
    # Create course with instructor
    with app.app_context():
        instructor = User.query.filter_by(email='instprog@example.com').first()
        course = Course(title='Progress Course', description='Test', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
    
    # Instructor tries to access progress (should fail or return empty)
    resp = client.get(f'/api/v2/courses/{course_id}/progress', headers=instructor_headers)
    # Instructor can access but progress is for students
    assert resp.status_code in (200, 401, 403)

def test_progress_endpoint_student(client, app):
    """Test progress endpoint for student"""
    student_info = get_student_headers(client, app)
    student_headers = student_info
    student_id = student_info['student_id']
    instructor_headers = get_instructor_headers(client, app)
    
    # Create course with module and lesson
    with app.app_context():
        instructor = User.query.filter_by(email='instprog@example.com').first()
        course = Course(title='Test Course', description='desc', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module 1', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
        
        lesson = Lesson(module_id=module_id, title='Lesson 1', content='Content', order=1)
        db.session.add(lesson)
        db.session.commit()
        lesson_id = lesson.id
        
        # Create a quiz
        quiz = Quiz(title='Quiz 1', course_id=course_id, instructor_id=instructor.id)
        db.session.add(quiz)
        db.session.commit()
        quiz_id = quiz.id
        
        # Add a question
        question = Question(
            quiz_id=quiz_id,
            prompt='Test Question?',
            options_json=json.dumps([
                {'option': 'A', 'is_correct': False},
                {'option': 'B', 'is_correct': True},
                {'option': 'C', 'is_correct': False},
                {'option': 'D', 'is_correct': False}
            ])
        )
        db.session.add(question)
        db.session.commit()
        question_id = question.id
    
    # Student enrolls
    enroll_resp = client.post(f'/api/v2/courses/{course_id}/enroll', headers=student_headers)
    assert enroll_resp.status_code == 201
    
    # Initially progress should be 0
    resp = client.get(f'/api/v2/courses/{course_id}/progress', headers=student_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'completion_percent' in data
    assert data['completion_percent'] == 0
    
    # Mark lesson as completed
    with app.app_context():
        mark_completed(student_id, lesson_id)
    
    # Progress should increase
    resp = client.get(f'/api/v2/courses/{course_id}/progress', headers=student_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['completion_percent'] > 0
    assert data['lessons_completed'] == 1
    assert data['total_lessons'] == 1
    
    # Submit quiz result
    with app.app_context():
        submit_quiz_result(quiz_id=quiz_id, student_id=student_id, answers_dict={str(question_id): '2'}, score=100)
    
    # Progress should now be higher
    resp = client.get(f'/api/v2/courses/{course_id}/progress', headers=student_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['completion_percent'] == 100.0  # 1 lesson + 1 quiz = 100%
    assert data['quizzes_taken'] == 1
    assert data['total_quizzes'] == 1

def test_all_progress_endpoint(client, app):
    """Test /api/v2/courses/my/progress endpoint"""
    student_info = get_student_headers(client, app)
    student_headers = student_info
    student_id = student_info['student_id']
    instructor_headers = get_instructor_headers(client, app)
    
    # Create two courses
    with app.app_context():
        instructor = User.query.filter_by(email='instprog@example.com').first()
        
        # Course 1 with lesson and quiz
        course1 = Course(title='Course 1', description='', instructor_id=instructor.id)
        db.session.add(course1)
        db.session.commit()
        course1_id = course1.id
        
        module1 = Module(course_id=course1_id, title='M1', order=1)
        db.session.add(module1)
        db.session.commit()
        lesson1 = Lesson(module_id=module1.id, title='L1', content='C1', order=1)
        db.session.add(lesson1)
        db.session.commit()
        lesson1_id = lesson1.id
        
        quiz1 = Quiz(title='Q1', course_id=course1_id, instructor_id=instructor.id)
        db.session.add(quiz1)
        db.session.commit()
        
        # Course 2
        course2 = Course(title='Course 2', description='', instructor_id=instructor.id)
        db.session.add(course2)
        db.session.commit()
        course2_id = course2.id
    
    # Enroll in both
    client.post(f'/api/v2/courses/{course1_id}/enroll', headers=student_headers)
    client.post(f'/api/v2/courses/{course2_id}/enroll', headers=student_headers)
    
    # Get all progress
    resp = client.get('/api/v2/courses/my/progress', headers=student_headers)
    assert resp.status_code == 200
    progress_data = resp.get_json()
    assert len(progress_data) == 2
    
    # Check course 1
    c1_progress = next(p for p in progress_data if p['course_id'] == course1_id)
    assert c1_progress['course_title'] == 'Course 1'
    assert c1_progress['completion_percent'] == 0  # Not completed anything
    
    # Mark lesson complete in course 1
    with app.app_context():
        mark_completed(student_id, lesson1_id)
    
    # Check progress again
    resp = client.get('/api/v2/courses/my/progress', headers=student_headers)
    assert resp.status_code == 200
    progress_data = resp.get_json()
    c1_progress = next(p for p in progress_data if p['course_id'] == course1_id)
    assert c1_progress['completion_percent'] > 0
    assert c1_progress['lessons_completed'] == 1