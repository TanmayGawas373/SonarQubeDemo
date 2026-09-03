import pytest
from app import create_app
from config.config import TestingConfig
from config.db import db
from models.user import User
from models.course import Course
from models.module import Module
from models.lesson import Lesson
from models.material import Material
from models.enrollment import Enrollment
from models.progress import Progress
from models.lesson_completion import LessonCompletion
from models.quiz import Quiz
from models.question import Question
from models.quiz_result import QuizResult

@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

def test_cascading_deletes(app):
    with app.app_context():
        # 1. Create Instructor and Student
        instructor = User(email='instructor@example.com', password_hash='hash', role='instructor', is_verified=True)
        student = User(email='student@example.com', password_hash='hash', role='student', is_verified=True)
        db.session.add_all([instructor, student])
        db.session.commit()

        # 2. Create Course
        course = Course(title='Flask Web Dev', description='Learn Flask', instructor_id=instructor.id)
        db.session.add(course)
        db.session.commit()

        # 3. Create Module
        module = Module(title='Introduction', course_id=course.id, order=1)
        db.session.add(module)
        db.session.commit()

        # 4. Create Lesson
        lesson = Lesson(title='First steps', module_id=module.id, order=1)
        db.session.add(lesson)
        db.session.commit()

        # 5. Create Lesson Completion
        completion = LessonCompletion(student_id=student.id, lesson_id=lesson.id)
        db.session.add(completion)
        db.session.commit()

        # 6. Create Material
        material = Material(module_id=module.id, file_path='flask.pdf', file_type='pdf', uploaded_by=instructor.id)
        db.session.add(material)
        db.session.commit()

        # 7. Create Enrollment and Progress
        enrollment = Enrollment(user_id=student.id, course_id=course.id)
        progress = Progress(student_id=student.id, course_id=course.id, completion_percent=50.0)
        db.session.add_all([enrollment, progress])
        db.session.commit()

        # 8. Create Quiz, Question, and QuizResult
        quiz = Quiz(title='Flask Quiz', course_id=course.id, instructor_id=instructor.id)
        db.session.add(quiz)
        db.session.commit()

        question = Question(quiz_id=quiz.id, prompt='What is Flask?')
        question.set_options([{'option': 'Microframework', 'is_correct': True}, {'option': 'CMS', 'is_correct': False}])
        
        quiz_result = QuizResult(quiz_id=quiz.id, student_id=student.id, score=100.0)
        quiz_result.set_answers({str(question.id): 0})
        
        db.session.add_all([question, quiz_result])
        db.session.commit()

        # Let's verify everything exists before deletions
        assert Course.query.get(course.id) is not None
        assert Module.query.get(module.id) is not None
        assert Lesson.query.get(lesson.id) is not None
        assert LessonCompletion.query.filter_by(student_id=student.id, lesson_id=lesson.id).first() is not None
        assert Material.query.get(material.id) is not None
        assert Enrollment.query.get(enrollment.id) is not None
        assert Progress.query.get(progress.id) is not None
        assert Quiz.query.get(quiz.id) is not None
        assert Question.query.get(question.id) is not None
        assert QuizResult.query.get(quiz_result.id) is not None

        # --- TEST 1: Delete Quiz cascades to Questions and QuizResults ---
        db.session.delete(quiz)
        db.session.commit()
        assert Quiz.query.get(quiz.id) is None
        assert Question.query.get(question.id) is None
        assert QuizResult.query.get(quiz_result.id) is None

        # Re-create quiz, question and result to test course cascading
        quiz = Quiz(title='Flask Quiz 2', course_id=course.id, instructor_id=instructor.id)
        db.session.add(quiz)
        db.session.commit()
        question = Question(quiz_id=quiz.id, prompt='What is Flask?')
        question.set_options([{'option': 'Microframework', 'is_correct': True}])
        quiz_result = QuizResult(quiz_id=quiz.id, student_id=student.id, score=100.0)
        quiz_result.set_answers({str(question.id): 0})
        db.session.add_all([question, quiz_result])
        db.session.commit()

        # --- TEST 2: Delete Lesson cascades to LessonCompletions ---
        db.session.delete(lesson)
        db.session.commit()
        assert Lesson.query.get(lesson.id) is None
        assert LessonCompletion.query.filter_by(student_id=student.id, lesson_id=lesson.id).first() is None

        # Re-create lesson and completion
        lesson = Lesson(title='First steps', module_id=module.id, order=1)
        db.session.add(lesson)
        db.session.commit()
        completion = LessonCompletion(student_id=student.id, lesson_id=lesson.id)
        db.session.add(completion)
        db.session.commit()

        # --- TEST 3: Delete Course cascades to Module, Lesson, Material, Enrollment, Progress, Quiz ---
        db.session.delete(course)
        db.session.commit()
        
        assert Course.query.get(course.id) is None
        assert Module.query.get(module.id) is None
        assert Lesson.query.get(lesson.id) is None
        assert LessonCompletion.query.filter_by(student_id=student.id, lesson_id=lesson.id).first() is None
        assert Material.query.get(material.id) is None
        assert Enrollment.query.get(enrollment.id) is None
        assert Progress.query.get(progress.id) is None
        assert Quiz.query.get(quiz.id) is None
        assert Question.query.get(question.id) is None
        assert QuizResult.query.get(quiz_result.id) is None
