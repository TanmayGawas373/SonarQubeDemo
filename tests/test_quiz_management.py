import pytest
import json
from app import create_app
from config.config import TestingConfig
from config.db import db
from models.user import User
from models.course import Course
from models.module import Module
from models.quiz import Quiz
from models.question import Question
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

def get_instructor_headers(client):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'instr@example.com',
        'password': 'Pass123',
        'role': 'instructor'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'instr@example.com',
        'password': 'Pass123'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def get_student_headers(client):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'stud3@example.com',
        'password': 'Pass123',
        'role': 'student'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'stud3@example.com',
        'password': 'Pass123'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def get_admin_headers(client):
    client.post('/api/v2/auth/register', json={
        'full_name': 'Test User',
        'education': 'Test Education',
        'email': 'admin_quiz@example.com',
        'password': 'AdminPass1',
        'role': 'admin'
    })
    resp = client.post('/api/v2/auth/login', json={
        'email': 'admin_quiz@example.com',
        'password': 'AdminPass1'
    })
    token = resp.get_json()['token']
    return {'Authorization': f'Bearer {token}'}

def test_quiz_creation_and_attempt_v2(client, app):
    """Test quiz creation and attempt via v2 endpoints"""
    instructor_headers = get_instructor_headers(client)
    student_headers = get_student_headers(client)
    
    # Create course and module with instructor
    with app.app_context():
        instructor = User.query.filter_by(email='instr@example.com').first()
        course = Course(title='QuizCourse', description='Course with quizzes', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Create a quiz
    quiz_resp = client.post(
        f'/api/v2/courses/{course_id}/quizzes',
        data=json.dumps({'title': 'Test Quiz'}),
        content_type="application/json",
        headers=instructor_headers
    )
    assert quiz_resp.status_code == 201
    quiz_id = json.loads(quiz_resp.data)['id']
    
    # Add questions to quiz
    question_data = {
        'prompt': 'What is 2+2?',
        'options': [
            {'option': '3', 'is_correct': False},
            {'option': '4', 'is_correct': True},
            {'option': '5', 'is_correct': False},
            {'option': '6', 'is_correct': False}
        ]
    }
    q_resp = client.post(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/questions',
        data=json.dumps(question_data),
        content_type="application/json",
        headers=instructor_headers
    )
    assert q_resp.status_code == 201
    question_id = q_resp.get_json()['id']
    
    # List quizzes
    list_resp = client.get(f'/api/v2/courses/{course_id}/quizzes', headers=student_headers)
    assert list_resp.status_code == 200
    quizzes = list_resp.get_json()
    assert any(q['title'] == 'Test Quiz' for q in quizzes)
    
    # List questions
    q_list_resp = client.get(f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/questions', headers=student_headers)
    assert q_list_resp.status_code == 200
    questions = q_list_resp.get_json()
    assert len(questions) == 1
    assert questions[0]['prompt'] == 'What is 2+2?'
    
    # Student enrolls in course
    enroll_resp = client.post(f'/api/v2/courses/{course_id}/enroll', headers=student_headers)
    assert enroll_resp.status_code == 201
    
    # Student attempts quiz
    attempt_resp = client.post(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/attempt',
        data=json.dumps({str(question_id): '1'}),  # option index 1 = '4' (correct)
        content_type="application/json",
        headers=student_headers
    )
    assert attempt_resp.status_code == 201
    result = attempt_resp.get_json()
    assert 'score' in result
    assert result['score'] == 100  # 100% for correct answer
    
    # View student results
    results_resp = client.get(f'/api/v2/courses/{course_id}/quizzes/my/results', headers=student_headers)
    assert results_resp.status_code == 200
    results = results_resp.get_json()
    assert 'results' in results
    assert len(results['results']) == 1
    assert results['results'][0]['score'] == 100

def test_quiz_admin_view_results(client, app):
    """Test admin can view all quiz results"""
    admin_headers = get_admin_headers(client)
    instructor_headers = get_instructor_headers(client)
    student_headers = get_student_headers(client)
    
    # Create course and module as instructor
    with app.app_context():
        instructor = User.query.filter_by(email='instr@example.com').first()
        course = Course(title='AdminQuizCourse', description='Test', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
        
        module = Module(course_id=course_id, title='Module', order=1)
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Create quiz
    quiz_resp = client.post(
        f'/api/v2/courses/{course_id}/quizzes',
        data=json.dumps({'title': 'Admin Quiz'}),
        content_type="application/json",
        headers=instructor_headers
    )
    quiz_id = json.loads(quiz_resp.data)['id']
    
    # Add question
    question_data = {
        'prompt': 'Capital of France?',
        'options': [
            {'option': 'London', 'is_correct': False},
            {'option': 'Paris', 'is_correct': True},
            {'option': 'Berlin', 'is_correct': False},
            {'option': 'Madrid', 'is_correct': False}
        ]
    }
    client.post(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/questions',
        data=json.dumps(question_data),
        content_type="application/json",
        headers=instructor_headers
    )
    
    # Student enrolls and attempts
    client.post(f'/api/v2/courses/{course_id}/enroll', headers=student_headers)
    client.post(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/attempt',
        data=json.dumps({'1': '1'}),  # correct answer
        content_type="application/json",
        headers=student_headers
    )
    
    # Admin views quiz results
    results_resp = client.get(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}/results',
        headers=admin_headers
    )
    assert results_resp.status_code == 200
    results = results_resp.get_json()
    assert len(results) == 1
    assert results[0]['score'] == 100

def test_quiz_update_delete_v2(client, app):
    """Test quiz update and delete via v2"""
    instructor_headers = get_instructor_headers(client)
    
    # Create course with instructor
    with app.app_context():
        instructor = User.query.filter_by(email='instr@example.com').first()
        course = Course(title='QuizCRUDCourse', description='Test', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()
        course_id = course.id
    
    # Create quiz
    quiz_resp = client.post(
        f'/api/v2/courses/{course_id}/quizzes',
        data=json.dumps({'title': 'Original Title'}),
        content_type="application/json",
        headers=instructor_headers
    )
    quiz_id = json.loads(quiz_resp.data)['id']
    
    # Update quiz
    upd_resp = client.put(
        f'/api/v2/courses/{course_id}/quizzes/{quiz_id}',
        data=json.dumps({'title': 'Updated Title'}),
        content_type="application/json",
        headers=instructor_headers
    )
    assert upd_resp.status_code == 200
    
    # Verify update
    get_resp = client.get(f'/api/v2/courses/{course_id}/quizzes/{quiz_id}', headers=instructor_headers)
    assert get_resp.status_code == 200
    assert get_resp.get_json()['title'] == 'Updated Title'
    
    # Delete quiz
    del_resp = client.delete(f'/api/v2/courses/{course_id}/quizzes/{quiz_id}', headers=instructor_headers)
    assert del_resp.status_code == 200
    
    # Verify deleted
    get_resp = client.get(f'/api/v2/courses/{course_id}/quizzes/{quiz_id}', headers=instructor_headers)
    assert get_resp.status_code == 404