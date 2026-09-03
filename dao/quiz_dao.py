# dao/quiz_dao.py
"""Data Access Object for quizzes, questions, and quiz results.
All functions are now methods of a class; wrappers preserve the old function names.
"""

from sqlalchemy import func
from config.db import db
from models.quiz import Quiz
from models.question import Question
from models.quiz_result import QuizResult


class QuizDAO:
    """Encapsulates database operations for quizzes, questions, and results."""

    # ---------- Quiz ----------
    def create_quiz(self, title, course_id, instructor_id):
        quiz = Quiz(title=title, course_id=course_id, instructor_id=instructor_id)
        db.session.add(quiz)
        db.session.commit()
        return quiz

    def get_quiz(self, quiz_id):
        return Quiz.query.get(quiz_id)

    def list_quizzes_by_course(self, course_id):
        return Quiz.query.filter_by(course_id=course_id).all()

    def delete_quiz(self, quiz_id):
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        db.session.delete(quiz)
        db.session.commit()
        return True

    # ---------- Question ----------
    def create_question(self, quiz_id, prompt, options):
        q = Question(prompt=prompt, quiz_id=quiz_id)
        q.set_options(options)
        db.session.add(q)
        db.session.commit()
        return q

    def get_question(self, question_id):
        return Question.query.get(question_id)

    def list_questions_by_quiz(self, quiz_id):
        return Question.query.filter_by(quiz_id=quiz_id).all()

    def delete_question(self, question_id):
        q = self.get_question(question_id)
        if not q:
            raise ValueError("Question not found")
        db.session.delete(q)
        db.session.commit()
        return True

    # ---------- QuizResult ----------
    def submit_quiz_result(self, quiz_id, student_id, answers_dict, score):
        result = QuizResult(
            quiz_id=quiz_id,
            student_id=student_id,
            score=score,
        )
        result.set_answers(answers_dict)
        db.session.add(result)
        db.session.commit()
        return result

    def get_quiz_result(self, result_id):
        return QuizResult.query.get(result_id)

    def list_results_by_quiz(self, quiz_id):
        return QuizResult.query.filter_by(quiz_id=quiz_id).all()

    def list_results_by_student(self, student_id):
        return QuizResult.query.filter_by(student_id=student_id).all()

    def get_quiz_results_by_student_and_course(self, student_id: int, course_id: int):
        """Return all QuizResult objects for a student in a specific course."""
        return (
            QuizResult.query.join(Quiz, QuizResult.quiz_id == Quiz.id)
            .filter(QuizResult.student_id == student_id, Quiz.course_id == course_id)
            .all()
        )

    def count_quizzes_by_instructor(self, instructor_id):
        return Quiz.query.filter_by(instructor_id=instructor_id).count()

    def average_score_by_instructor(self, instructor_id):
        result = (
            db.session.query(func.avg(QuizResult.score))
            .join(Quiz, QuizResult.quiz_id == Quiz.id)
            .filter(Quiz.instructor_id == instructor_id)
            .scalar()
        )
        return round(float(result), 2) if result is not None else 0.0

    def update_quiz_title(self, quiz_id, title):
        quiz = self.get_quiz(quiz_id)
        if not quiz:
            raise ValueError("Quiz not found")
        quiz.title = title
        db.session.commit()
        return quiz

    def update_question(self, question_id, prompt, options):
        q = self.get_question(question_id)
        if not q:
            raise ValueError("Question not found")
        q.prompt = prompt
        q.set_options(options)
        db.session.commit()
        return q

    def get_student_results_paginated(self, student_id: int, page: int = 1, per_page: int = 10, search: str = None):
        """Return paginated quiz results for a student with quiz and course info."""
        from models.quiz import Quiz
        from models.course import Course
        
        query = (
            db.session.query(QuizResult, Quiz, Course)
            .join(Quiz, QuizResult.quiz_id == Quiz.id)
            .join(Course, Quiz.course_id == Course.id)
            .filter(QuizResult.student_id == student_id)
        )
        
        if search:
            query = query.filter(Quiz.title.ilike(f"%{search}%"))
        
        total_count = query.count()
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        
        results = (
            query.order_by(QuizResult.submitted_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )
        
        return {
            'results': results,
            'total_count': total_count,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page
        }

    def get_instructor_quiz_results_paginated(self, instructor_id: int, page: int = 1, per_page: int = 10, search: str = None):
        """Return paginated quiz results for an instructor's courses with student info."""
        from models.quiz import Quiz
        from models.course import Course
        from models.user import User
        
        query = (
            db.session.query(QuizResult, User, Quiz, Course)
            .join(User, QuizResult.student_id == User.id)
            .join(Quiz, QuizResult.quiz_id == Quiz.id)
            .join(Course, Quiz.course_id == Course.id)
            .filter(Course.instructor_id == instructor_id)
        )
        
        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        
        total_count = query.count()
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        
        results = (
            query.order_by(QuizResult.submitted_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )
        
        return {
            'results': results,
            'total_count': total_count,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page
        }

    def get_instructor_students(self, instructor_id: int):
        """Return students enrolled in instructor's courses."""
        from models.enrollment import Enrollment
        from models.user import User
        from models.course import Course
        
        return (
            db.session.query(Enrollment, User, Course)
            .join(User, Enrollment.user_id == User.id)
            .join(Course, Enrollment.course_id == Course.id)
            .filter(Course.instructor_id == instructor_id)
            .all()
        )

    def get_instructor_students_paginated(self, instructor_id: int, page: int = 1, per_page: int = 10, search: str = None):
        """Return paginated students enrolled in instructor's courses with search."""
        from models.enrollment import Enrollment
        from models.user import User
        from models.course import Course
        
        query = (
            db.session.query(Enrollment, User, Course)
            .join(User, Enrollment.user_id == User.id)
            .join(Course, Enrollment.course_id == Course.id)
            .filter(Course.instructor_id == instructor_id)
        )
        
        if search:
            query = query.filter(User.email.ilike(f"%{search}%"))
        
        total_count = query.count()
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        
        results = (
            query.order_by(Enrollment.enrolled_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )
        
        return {
            'results': results,
            'total_count': total_count,
            'total_pages': total_pages,
            'page': page,
            'per_page': per_page
        }


# Module‑level singleton for easy import
quiz_dao = QuizDAO()

# Backward‑compatible wrappers (function style)
def create_quiz(*args, **kwargs):
    return quiz_dao.create_quiz(*args, **kwargs)

def get_quiz(*args, **kwargs):
    return quiz_dao.get_quiz(*args, **kwargs)

def list_quizzes_by_course(*args, **kwargs):
    return quiz_dao.list_quizzes_by_course(*args, **kwargs)

def delete_quiz(*args, **kwargs):
    return quiz_dao.delete_quiz(*args, **kwargs)

def create_question(*args, **kwargs):
    return quiz_dao.create_question(*args, **kwargs)

def get_question(*args, **kwargs):
    return quiz_dao.get_question(*args, **kwargs)

def list_questions_by_quiz(*args, **kwargs):
    return quiz_dao.list_questions_by_quiz(*args, **kwargs)

def delete_question(*args, **kwargs):
    return quiz_dao.delete_question(*args, **kwargs)

def submit_quiz_result(*args, **kwargs):
    return quiz_dao.submit_quiz_result(*args, **kwargs)

def get_quiz_result(*args, **kwargs):
    return quiz_dao.get_quiz_result(*args, **kwargs)

def list_results_by_quiz(*args, **kwargs):
    return quiz_dao.list_results_by_quiz(*args, **kwargs)

def list_results_by_student(*args, **kwargs):
    return quiz_dao.list_results_by_student(*args, **kwargs)

def get_quiz_results_by_student_and_course(*args, **kwargs):
    return quiz_dao.get_quiz_results_by_student_and_course(*args, **kwargs)

def count_quizzes_by_instructor(*args, **kwargs):
    return quiz_dao.count_quizzes_by_instructor(*args, **kwargs)

def average_score_by_instructor(*args, **kwargs):
    return quiz_dao.average_score_by_instructor(*args, **kwargs)

def update_quiz_title(*args, **kwargs):
    return quiz_dao.update_quiz_title(*args, **kwargs)

def update_question(*args, **kwargs):
    return quiz_dao.update_question(*args, **kwargs)

def get_student_results_paginated(*args, **kwargs):
    return quiz_dao.get_student_results_paginated(*args, **kwargs)

def get_instructor_quiz_results_paginated(*args, **kwargs):
    return quiz_dao.get_instructor_quiz_results_paginated(*args, **kwargs)

def get_instructor_students(*args, **kwargs):
    return quiz_dao.get_instructor_students(*args, **kwargs)

def get_instructor_students_paginated(*args, **kwargs):
    return quiz_dao.get_instructor_students_paginated(*args, **kwargs)
